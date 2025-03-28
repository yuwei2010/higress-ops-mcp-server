from typing import Dict, List, Any
import logging
from utils.higress_client import HigressClient

class RequestBlockTools:
    """Tool class for managing request block plugins.
    
    Attributes:
        logger: Logger instance for logging (set by ToolsRegister)
        higress_client: HigressClient instance for API calls (set by ToolsRegister)
    """
    
    def register_tools(self, mcp: Any):
        @mcp.tool()
        async def update_request_block_plugin(enabled: bool, configurations: Dict, scope: str, resource_name: str = None) -> Dict:
            """
            Update the configuration for the request-block plugin.
            
            Args:
                enabled: bool: Whether the plugin is enabled
                configurations: Dict[str, Any] containing the following keys:
                - block_bodies: List[str]: Strings to block in the request body
                - block_headers: List[str]: Strings to block in the request header
                - block_urls: List[str]: Strings to block in the request URL
                - blocked_code: int: HTTP status code to return when a block is matched
                - case_sensitive: bool: Whether the block matching is case sensitive
                scope: The scope at which the plugin is applied. Must be one of: 
                      "global", "domain", "service", or "route"
                resource_name: The name of the resource (required for domain, service, route scopes)
                
            Returns:
                Updated plugin data
                
            Raises:
                ValueError: If scope is not specified or resource_name is not provided for non-global scopes

            Example:
            {
                "block_bodies": [
                    "hello world"
                ],
                "block_headers": [
                    "example-key",
                    "example-value"
                ],
                "block_urls": [
                    "seven.html"
                ],
                "blocked_code": 404,
                "case_sensitive": false
            }
                
            """
            name = "request-block"
            self.logger.info(f"Update request-block plugin at {scope} scope" + 
                          (f" for {resource_name}" if resource_name else "") + 
                          f" with configurations: {configurations}")
            return self.higress_client.update_plugin(name, enabled, configurations, scope, resource_name)
