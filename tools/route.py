from typing import Dict, List, Any
from fastmcp import FastMCP

class RouteTools:
    def register_tools(self, mcp: FastMCP):
        @mcp.tool()
        async def list_routes() -> List[Dict]:
            """
            List all available routes.
            
            Returns:
                List of route data as dictionaries
            
            Raises:
                ValueError: If the request fails
            """
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
            return self.higress_client.get_route(name)
            
        @mcp.tool()
        async def add_route(configurations: Dict[str, Any]) -> Dict:
            """
            Add a new route. The 3 required fields in the configurations are name, path, services.

            Args:
                configurations: Dict[str, Any] containing the following keys:
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
            return self.higress_client.add_route(configurations)

        @mcp.tool()
        async def update_route(name: str, configurations: Dict[str, Any]) -> Dict:
            """
            Update an existing route. Only provide the fields you want to update.
            
            Args:
                name: The name of the route (required)
                configurations: Dict[str, Any] containing the following keys:
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
            return self.higress_client.update_route(name, configurations)
