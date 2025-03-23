import asyncio
import json
import uuid
from os import getenv
from typing import TypedDict, Annotated, List

from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.graph.message import add_messages
from utils.graph import draw_graph

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from utils.tools_handler import create_tool_node_with_fallback, print_event

# Define write operations that require confirmation
SENSITIVE_TOOLS = ["update_request_block_plugin"]

class State(TypedDict):
    """State for the chat application."""
    messages: Annotated[List, add_messages]

class HigressAssistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            # 创建了一个无限循环，它将一直执行直到：从 self.runnable 获取的结果是有效的。
            # 如果结果无效（例如，没有工具调用且内容为空或内容不符合预期格式），循环将继续执行，
            result = self.runnable.invoke(state["messages"])
            # 如果，runnable执行完后，没有得到一个实际的输出
            if not result.tool_calls and (  # 如果结果中没有工具调用，并且内容为空或内容列表的第一个元素没有"text"，则需要重新提示用户输入。
                    not result.content
                    or isinstance(result.content, list)
                    and not result.content[0].get("text")
            ):
                messages = state["messages"] + [HumanMessage(content="请提供一个真实的输出作为回应。")]
                state = {**state, "messages": messages}
            else:  # 如果： runnable执行后已经得到，想要的输出，则退出循环
                break
        return {'messages': result}


# Create assistant node
def create_assistant_node(tools):
    """Create the assistant node that uses the LLM to generate responses."""
    # Create a model instance
    llm = ChatOpenAI(
        openai_api_key=getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        model_name="openai/gpt-4o",
    )
    
    # System prompt with instruction to get current plugin config before updating
    system_prompt = (
        """
        When updating a plugin configuration with `update_request_block_plugin`, 
        ALWAYS first call `get_plugin` to retrieve the current configuration before making any changes. 
        This ensures that only the specified parameters are updated while preserving the existing configuration values.
        """
    )
    
    # Apply system prompt to LLM
    llm_with_prompt = llm.bind(system_prompt=system_prompt)

    # Bind tools to the LLM with the system prompt
    llm_with_tools = llm_with_prompt.bind_tools(tools)

    return HigressAssistant(llm_with_tools)
    

# Function to route tools based on whether they are read or write operations
def route_conditional_tools(state: State) -> str:
    """Route to the appropriate tool node based on the tool type."""
    print("Route conditional tools.......")
    print("State:", state)
    next_node = tools_condition(state)
    if next_node == END:
        print("Route to END........")
        return END
    
    ai_message = state["messages"][-1]
    tool_call = ai_message.tool_calls[0]
    
    if tool_call["name"] in SENSITIVE_TOOLS:
        print("Route to sensitive tools........")
        return "sensitive_tools"
    print("Route to safe tools........")
    return "safe_tools"

async def build_and_run_graph(tools):
    """Build and run the LangGraph."""
    
    # Categorize tools
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
    draw_graph(graph, "graph.png")
    
    # Create a session ID
    session_id = str(uuid.uuid4())
    
    # Configuration for the graph
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }
    
    printed_set = set()  # To avoid duplicate prints
    
    print("\nMCP Client Started!")
    print("Type your queries or 'quit' to exit.")
    
    # Main interaction loop
    while True:
        try:
            query = input("\n用户: ")
            # 检查输入是否完整
            print(f"收到输入: {query}")
        except Exception as e:
            print(f"输入处理错误: {e}")
            continue
        if query.lower() in ["q", "exit", "quit"]:
            print("对话结束，拜拜！")
            break
        
        # Create initial state with user message
        initial_state = {"messages": [HumanMessage(content=query)]}
        
        # Stream the events
        events = graph.astream(initial_state, config, stream_mode="values")
        
        # Print the events
        async for event in events:
            print_event(event, printed_set)
        
        # Check if we need user confirmation
        current_state = graph.get_state(config)
        print("########### Current state:", current_state)
        if current_state.next:
            user_input = input("\n您是否批准上述操作？输入'y'继续；否则，请说明您请求的更改: ")
            if user_input.strip().lower() == "y":
                # Continue execution
                events = graph.astream(None, config, stream_mode="values")
                async for event in events:
                    print_event(event, printed_set)
            else:
                # Reject the tool call with user's reason
                tool_call_id = current_state.values["messages"][-1].tool_calls[0]["id"]
                rejection_state = {
                    "messages": [
                            ToolMessage(
                                tool_call_id=tool_call_id,
                                content=f"操作被用户拒绝。原因: '{user_input}'。",
                            )
                        ]
                    }
                result = graph.astream(rejection_state, config, stream_mode="values")
                async for event in result:
                    print_event(event, printed_set)

async def main():
    """Main function to run the MCP client."""
    server_params = StdioServerParameters(
        command="python",
        args=["./server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Get available tools
            response = await session.list_tools()
            print("Connected to MCP server successfully!")
            print("Available tools:", [tool.name for tool in response.tools])
            
            # Load tools for LangChain
            tools = await load_mcp_tools(session)
            
            # Build and run the graph
            await build_and_run_graph(tools)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())