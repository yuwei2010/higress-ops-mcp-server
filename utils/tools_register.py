import logging
from typing import Any, List, Type
from utils.higress_client import HigressClient

class ToolsRegister:
    """
    A class responsible for creating and registering all tool classes.
    This centralizes the tool registration process and reduces duplication.
    """
    
    def __init__(self, logger: logging.Logger, higress_client: HigressClient, mcp: Any):
        """
        Initialize the tools registrar.
        
        Args:
            logger: Logger instance for logging
            higress_client: HigressClient instance for API calls
            mcp: FastMCP instance for tool registration
        """
        self.logger = logger
        self.higress_client = higress_client
        self.mcp = mcp
        
    def register_all_tools(self, tool_classes: List[Type]):
        """
        Create instances of all tool classes and register their tools.
        
        Args:
            tool_classes: List of tool classes to instantiate and register
        """
        for tool_class in tool_classes:
            # Create an instance of the tool class without initialization parameters
            tool_instance = tool_class()
            
            # Set logger and higress_client attributes directly
            tool_instance.logger = self.logger
            tool_instance.higress_client = self.higress_client
            
            # Register the tools from this instance
            tool_instance.register_tools(self.mcp)
            
            self.logger.info(f"Registered tools from {tool_class.__name__}")
