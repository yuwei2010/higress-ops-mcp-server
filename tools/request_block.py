from typing import Dict, List, Any
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
                configurations: Dict[str, Any] containing the following keys:
                - block_bodies: List[str]: Strings to block in the request body
                - block_headers: List[str]: Strings to block in the request header
                - block_urls: List[str]: Strings to block in the request URL
                - blocked_code: int: HTTP status code to return when a block is matched
                - case_sensitive: bool: Whether the block matching is case sensitive

                Here is an example:
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
                
            Returns:
                Updated plugin data
            """
            name = "request-block"
            self.logger.info(f"Update request-block plugin with configurations: {configurations}")
            return self.higress_client.update_plugin(name, configurations)
