from typing import Dict, Any
import logging
from utils.higress_client import HigressClient

class CommonTools:
    def __init__(self, logger: logging.Logger, higress_client: HigressClient):
        """Initialize CommonTools with logger and higress client.
        
        Args:
            logger: Logger instance for logging
            higress_client: HigressClient instance for API calls
        """
        self.logger = logger
        self.higress_client = higress_client
    
    def register_tools(self, mcp: Any):
        """Register common tools."""

        @mcp.tool()
        async def get_plugin(name: str) -> Dict:
            """Get detailed information about a specific Higress plugin.
            
            Args:
                name: The name of the plugin
                
            Returns:
                Plugin data as a dictionary
                
            Raises:
                ValueError: If the plugin is not found or the request fails
            """
            self.logger.info(f"Get plugin: {name}")
            return self.higress_client.get_plugin(name)