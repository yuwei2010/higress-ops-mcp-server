from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode

def handle_tool_error(state) -> dict:
    """
    Handle errors that occur during tool calls.

    Args:
        state (dict): Current state dictionary containing error information and message list.

    Returns:
        dict: Dictionary with a new message list containing error information.
    """
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls  # Get all tool calls from the last message
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\nPlease correct your error.",
                tool_call_id=tc["id"],  # Link to the ID of the tool call that caused the error
            )
            for tc in tool_calls  # Iterate through all tool calls and generate corresponding messages
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    """
    Create a tool node with fallback mechanism. 
    When a specified tool fails to execute (e.g., throws an exception),
    the fallback operation will be triggered.

    Args:
        tools (list): List of tools.

    Returns:
        dict: Tool node with fallback mechanism.
    """
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def print_event(event: dict, _printed: set):
    """
    Print event information, especially dialog states and message content.

    Args:
        event (dict): Event dictionary containing dialog state and messages.
        _printed (set): Set of printed message IDs to avoid duplicate printing.
    """
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            print(msg_repr)
            # Add the printed message ID to the set
            _printed.add(message.id)
