from typing import Dict, List, Any
import logging
from utils.higress_client import HigressClient

class RouteTools:
    def __init__(self, logger: logging.Logger, higress_client: HigressClient):
        """
        Initialize RouteTools with logger and higress client.
        
        Args:
            logger: Logger instance for logging
            higress_client: HigressClient instance for API calls
        """
        self.logger = logger
        self.higress_client = higress_client
    
    def register_tools(self, mcp: Any):
        """
        Register route-related tools with the MCP server.
        """
        
        @mcp.tool()
        async def list_routes() -> List[Dict]:
            """
            List all available routes in Higress.
            
            Returns:
                List of route data as dictionaries
            
            Raises:
                ValueError: If the request fails
            """
            self.logger.info("Listing all routes")
            return self.higress_client.list_routes()
            
        @mcp.tool()
        async def get_route(name: str) -> Dict:
            """
            Get detailed information about a specific route.
            
            Args:
                name: The name of the route
                
            Returns:
                Route data as a dictionary
                
            Raises:
                ValueError: If the route is not found or the request fails
            """
            self.logger.info(f"Getting route: {name}")
            return self.higress_client.get_route(name)
