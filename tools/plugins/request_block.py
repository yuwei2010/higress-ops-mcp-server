from typing import Dict
from fastmcp import FastMCP

class RequestBlockTools:
    def register_tools(self, mcp: FastMCP):
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
            return self.higress_client.update_plugin(name, enabled, configurations, scope, resource_name)
