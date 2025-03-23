from typing import Dict, Any
import logging
from utils.higress_client import HigressClient

class RequestBlockTools:
    def __init__(self, logger: logging.Logger, higress_client: HigressClient):
        """Initialize RequestBlockTools with logger and higress client.
        
        Args:
            logger: Logger instance for logging
            higress_client: HigressClient instance for API calls
        """
        self.logger = logger
        self.higress_client = higress_client
    
    def register_tools(self, mcp: Any):
        @mcp.tool()
        async def update_request_block_plugin(configurations: Dict) -> Dict:
            """
            Update the configuration for the request-block plugin.
            
            Args:
                configurations: The new configuration for the plugin
                configuration is a dictionary with the following keys:
                    block_bodies: List of strings to block in the request body
                    block_headers: List of strings to block in the request header
                    block_urls: List of strings to block in the request URL
                    blocked_code: The HTTP status code to return when a block is matched
                    case_sensitive: Boolean to determine if the block is case sensitive
                At least one of block_urls, block_headers, or block_bodies is required.

                Here is an example:
                    "configurations": {
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
                
            Returns:
                Updated plugin data
            """
            name = "request-block"
            self.logger.info(f"Update request-block plugin with configurations: {configurations}")
            return self.higress_client.update_plugin(name, configurations)
