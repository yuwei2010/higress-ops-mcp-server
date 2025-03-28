from typing import Dict, Any
import logging
from utils.higress_client import HigressClient

class CommonTools:
    """Tool class for common operations.
    
    Attributes:
        logger: Logger instance for logging (set by ToolsRegister)
        higress_client: HigressClient instance for API calls (set by ToolsRegister)
    """
    
    def register_tools(self, mcp: Any):
        """Register common tools."""

        @mcp.tool()
        async def get_plugin(name: str, scope: str, resource_name: str = None) -> Dict:
            """Get detailed information about a specific Higress plugin.
            
            Args:
                name: The name of the plugin
                scope: The scope at which the plugin is applied. Must be one of: 
                      "global", "domain", "service", or "route"
                resource_name: The name of the resource (required for domain, service, route scopes)
                
            Returns:
                Plugin data as a dictionary
                
            Raises:
                ValueError: If the plugin is not found, the request fails, scope is not specified,
                           or resource_name is missing for non-global scopes
            """
            self.logger.info(f"Get plugin: {name} at {scope} scope" + (f" for {resource_name}" if resource_name else ""))
            return self.higress_client.get_plugin(name, scope, resource_name)