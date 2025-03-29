import asyncio
import logging
import uuid
from os import getenv
from typing import Annotated, List, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from utils.params import parse_args, validate
from tools.handler import create_tool_node_with_fallback, print_event

# Define write operations that require human confirmation
SENSITIVE_TOOLS = [
    "add_route", 
    "add_service_source",
    "update_route",
    "update_request_block_plugin", 
    "update_service_source", 
]

class State(TypedDict):
    """State for the chat application."""
    messages: Annotated[List, add_messages]

class HigressAssistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        result = self.runnable.invoke(state["messages"])
        return {'messages': result}

def create_assistant_node(tools):
    """Create the assistant node that uses the LLM to generate responses."""
    llm = ChatOpenAI(
        openai_api_key=getenv("OPENAI_API_KEY"),
        openai_api_base=getenv("OPENAI_API_BASE"),
        model_name=getenv("MODEL_NAME"),
    )
    
    llm_with_tools = llm.bind_tools(tools)
    return HigressAssistant(llm_with_tools)
    

def route_conditional_tools(state: State) -> str:
    """Route to the appropriate tool node based on the tool type."""
    next_node = tools_condition(state)
    if next_node == END:
        return END
    
    ai_message = state["messages"][-1]
    tool_call = ai_message.tool_calls[0]
    
    if tool_call["name"] in SENSITIVE_TOOLS:
        return "sensitive_tools"
    return "safe_tools"

async def build_and_run_graph(tools):
    """Build and run the LangGraph."""
    sensitive_tools = []
    safe_tools = []
    for tool in tools:
        if tool.name in SENSITIVE_TOOLS:
            sensitive_tools.append(tool)
        else:
            safe_tools.append(tool)
    
    # Create the graph builder
    builder = StateGraph(State)
    
    # Add nodes
    builder.add_node("assistant", create_assistant_node(tools))
    builder.add_node("safe_tools", create_tool_node_with_fallback(safe_tools))
    builder.add_node("sensitive_tools", create_tool_node_with_fallback(sensitive_tools))
    
    # Add edges
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        route_conditional_tools,
        ["safe_tools", "sensitive_tools", END]
    )
    builder.add_edge("safe_tools", "assistant")
    builder.add_edge("sensitive_tools", "assistant")
    
    # Compile the graph
    memory = MemorySaver()
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["sensitive_tools"],
    )

    # Draw the graph
    # draw_graph(graph, "graph.png")
    
    # Create a session ID
    session_id = str(uuid.uuid4())
    
    # Configuration for the graph
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }
    
    # To avoid duplicate prints
    printed_set = set()  
    
    logging.info("MCP Client Started!")
    print("Type your queries or 'quit' to exit.")
    
    # Main interaction loop
    while True:
        try:
            query = input("\nUser: ")
        except Exception as e:
            logging.error(f"Input processing error: {e}")
            continue
        if query.lower() in ["q", "exit", "quit"]:
            logging.info("Conversation ended, goodbye!")
            break
        
        # Create initial state with user message
        initial_state = {"messages": [HumanMessage(content=query)]}
        
        # Stream the events
        events = graph.astream(initial_state, config, stream_mode="values")
        
        # Print the events
        async for event in events:
            print_event(event, printed_set)
        
        # Process tool calls and confirmations recursively
        await process_tool_calls(graph, config, printed_set)

async def process_tool_calls(graph, config, printed_set):
    """Process tool calls recursively, asking for user confirmation when needed."""
    current_state = graph.get_state(config)
    
    # If there's a next node, we need user confirmation
    if current_state.next:
        # Check if the last message contains tool calls that need confirmation
        last_message = current_state.values["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            # Get the tool name from the tool call
            tool_name = last_message.tool_calls[0].get("name", "")
            
            # Only ask for confirmation for sensitive operations
            if tool_name in SENSITIVE_TOOLS:
                user_input = input("\nDo you approve the above operation? Enter 'y' to continue; otherwise, please explain your requested changes: ")
                
                if user_input.strip().lower() == "y":
                    # Continue execution
                    events = graph.astream(None, config, stream_mode="values")
                    async for event in events:
                        print_event(event, printed_set)
                    
                    # Process any subsequent tool calls
                    await process_tool_calls(graph, config, printed_set)
                else:
                    # Reject the tool call with user's reason
                    tool_call_id = last_message.tool_calls[0]["id"]
                    rejection_state = {
                        "messages": [
                            ToolMessage(
                                tool_call_id=tool_call_id,
                                content=f"Operation rejected by user. Reason: '{user_input}'.",
                            )
                        ]
                    }
                    
                    # Process the rejection
                    events = graph.astream(rejection_state, config, stream_mode="values")
                    async for event in events:
                        print_event(event, printed_set)
                    
                    # Process any subsequent tool calls that might be generated after rejection
                    await process_tool_calls(graph, config, printed_set)
            else:
                # For non-sensitive tools, continue without confirmation
                events = graph.astream(None, config, stream_mode="values")
                async for event in events:
                    print_event(event, printed_set)
                
                # Process any subsequent tool calls
                await process_tool_calls(graph, config, printed_set)

async def main():
    """Main function to run the MCP client."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("higress-mcp-client")
    
    # Parse command line arguments
    args = parse_args("Higress MCP Client")
    
    # Prepare server arguments
    server_args = ["./server.py"]
    
    # Get and validate credentials
    higress_url, username, password = validate(
        higress_url=args.higress_url,
        username=args.username,
        password=args.password
    )
    
    # Add parameters to server arguments
    if higress_url:
        server_args.extend(["--higress-url", higress_url])
    server_args.extend(["--username", username])
    server_args.extend(["--password", password])
    
    server_params = StdioServerParameters(
        command="python",
        args=server_args,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Get available tools
            response = await session.list_tools()
            logger.info("Connected to MCP server successfully!")
            logger.info(f"Available tools: {[tool.name for tool in response.tools]}")
            
            # Load tools for LangChain
            tools = await load_mcp_tools(session)
            
            # Build and run the graph
            await build_and_run_graph(tools)

# Run the async main function
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    asyncio.run(main())