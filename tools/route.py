from typing import Dict, List, Any
import logging
from utils.higress_client import HigressClient

class RouteTools:
    """Tool class for managing Higress routes.
    
    Attributes:
        logger: Logger instance for logging (set by ToolsRegister)
        higress_client: HigressClient instance for API calls (set by ToolsRegister)
    """
    
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
            
        @mcp.tool()
        async def add_route(route_config: Dict[str, Any]) -> Dict:
            """
            Add a new route. The 3 required fields in the route_config are name, path, services.

            Args:
                route_config: Dict[str, Any] containing the following keys:
                    - name (required): The name of the route
                    - path (required): Dict[str, Any]: The path configuration with keys:
                        - matchType: str: Match type (PRE, EQUAL, REGULAR)
                        - matchValue: str: Value to match
                        - caseSensitive: bool: Whether matching is case sensitive
                    - services (required): List[Dict[str, Any]]: List of services for this route with keys:
                        - name: str: Service name
                        - port: int: Service port
                        - weight: int: Service weight
                    - domains: List[str]: List of domain names, but only one domain is allowed
                    - methods: List[str]: List of HTTP methods (GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH, TRACE, CONNECT)
                    - headers: List[Dict[str, Any]]: List of header match conditions with keys:
                        - matchType: str: Match type (PRE, EQUAL, REGULAR)
                        - matchValue: str: Value to match
                        - caseSensitive: bool: Whether matching is case sensitive
                        - key: str: Header key name
                    - urlParams: List[Dict[str, Any]]: List of URL parameter match conditions with keys:
                        - matchType: str: Match type (PRE, EQUAL, REGULAR)
                        - matchValue: str: Value to match
                        - caseSensitive: bool: Whether matching is case sensitive
                        - key: str: Parameter key name
                    - customConfigs: Dict[str, str]: Dictionary of custom configurations
                    
            Returns:
                The updated route configuration
            
            Raises:
                ValueError: If the request fails or required fields are missing

            Example:
                {
                    "name": "route-example",
                    "domains": ["example.com"],
                    "path": {
                        "matchType": "PRE",
                        "matchValue": "/test",
                        "caseSensitive": true
                    },
                    "methods": ["GET", "POST"],
                    "headers": [
                        {
                            "matchType": "EQUAL",
                            "matchValue": "test2",
                            "caseSensitive": null,
                            "key": "header2"
                        },
                        {
                            "matchType": "PRE",
                            "matchValue": "test1",
                            "caseSensitive": null,
                            "key": "header1"
                        },
                        {
                            "matchType": "REGULAR",
                            "matchValue": "test3.*",
                            "caseSensitive": null,
                            "key": "header3"
                        }
                    ],
                    "urlParams": [
                        {
                            "matchType": "PRE",
                            "matchValue": "value1",
                            "caseSensitive": null,
                            "key": "query1"
                        }
                    ],
                    "services": [
                        {
                            "name": "seven-test.dns",
                            "port": 443,
                            "weight": 100
                        }
                    ],
                    "customConfigs": {
                        "annotation1": "value1"
                    }
                }
            """
            return self.higress_client.add_route(route_config)

        @mcp.tool()
        async def update_route(route_name: str, route_config: Dict[str, Any]) -> Dict:
            """
            Update an existing route. Only provide the fields you want to update.
            
            Args:
                route_name: The name of the route (required)
                route_config: Dict[str, Any] containing the following keys:
                    - path: Dict[str, Any]: The path configuration with keys:
                        - matchType: str: Match type (PRE, EQUAL, REGULAR)
                        - matchValue: str: Value to match
                        - caseSensitive: bool: Whether matching is case sensitive
                    - services: List[Dict[str, Any]]: List of services for this route with keys:
                        - name: str: Service name
                        - port: int: Service port
                        - weight: int: Service weight
                    - domains: List[str]: List of domain names, but only one domain is allowed
                    - methods: List[str]: List of HTTP methods (GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH, TRACE, CONNECT)
                    - headers: List[Dict[str, Any]]: List of header match conditions with keys:
                        - matchType: str: Match type (PRE, EQUAL, REGULAR)
                        - matchValue: str: Value to match
                        - caseSensitive: bool: Whether matching is case sensitive
                        - key: str: Header key name
                    - urlParams: List[Dict[str, Any]]: List of URL parameter match conditions with keys:
                        - matchType: str: Match type (PRE, EQUAL, REGULAR)
                        - matchValue: str: Value to match
                        - caseSensitive: bool: Whether matching is case sensitive
                        - key: str: Parameter key name
                    - customConfigs: Dict[str, str]: Dictionary of custom configurations
                    
            Returns:
                The updated route configuration
            
            Raises:
                ValueError: If the request fails or required fields are missing

            Example:
                {
                    "path": {
                        "matchType": "PRE",
                        "matchValue": "/test",
                        "caseSensitive": true
                    },
                    "methods": ["GET", "POST"],
                }
            """
            return self.higress_client.update_route(route_config)
