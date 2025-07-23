# tools/registry.py
from langchain_core.tools import Tool
from .tool_booking import make_tool as make_booking_tool
# Add more tools below when needed:
# from .tool_leave import make_tool as make_leave_tool

def load_all_tools(user_id: str) -> list[Tool]:
    """
    Manually loads all tools defined here.
    Each tool must have a `make_tool(user_id)` function.
    """
    tools = []

    try:
        tool = make_booking_tool(user_id)
        tools.append(tool)
        print("✅ Loaded tool: tool_booking")
    except Exception as e:
        print(f"❌ Failed to load tool_booking: {e}")

    # Example for more tools:
    # try:
    #     tool = make_leave_tool(user_id)
    #     tools.append(tool)
    #     print("✅ Loaded tool: tool_leave")
    # except Exception as e:
    #     print(f"❌ Failed to load tool_leave: {e}")

    return tools
