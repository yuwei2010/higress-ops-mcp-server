import logging
import requests
from typing import Dict, List, Any

class HigressClient:
    """Client for interacting with Higress Console API."""
    
    def __init__(self, logger: logging.Logger, username: str, password: str, higress_url: str):
        """Initialize the Higress client.
        
        Args:
            logger: Logger instance for logging requests and responses
            username: Username for basic authentication (required)
            password: Password for basic authentication (required)
            higress_url: Higress URL for the API, defaults to 'http://localhost:8001'
        """
        self.logger = logger
        self.higress_url = higress_url    
        self.auth = (username, password)
        
    def _process_response(self, response: requests.Response, method: str, path: str) -> Dict[str, Any]:
        """Process the API response and handle success/error cases.
        
        Args:
            response: The HTTP response object
            method: The HTTP method (GET, POST, PUT)
            path: The API path
            
        Returns:
            The response data
            
        Raises:
            ValueError: If the API returns success=false
        """
        response.raise_for_status()
        response_json = response.json()
        self.logger.info(f"{method} {path} response: {response_json}")

        # If success field exists and is False, it indicates an error
        if "success" in response_json and response_json["success"] == False:
            error_msg = response_json.get("message", "Unknown API error")
            self.logger.error(f"Request API error for {method} {path}: {error_msg}")
            raise ValueError(f"Request API error for {method} {path}: {error_msg}")

        return response_json.get("data", response_json)

    def get(self, path: str) -> Dict[str, Any]:
        """Make a GET request to the Higress Console API.
        
        Args:
            path: API path
            
        Returns:
            Response data as a dictionary
            
        Raises:
            ValueError: If the request fails or the API returns success=false
        """
        url = f"{self.higress_url}{path}"
        self.logger.info(f"GET request to: {url}")
        
        response = requests.get(url, auth=self.auth)
        return self._process_response(response, "GET", path)


    def post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the Higress Console API.
        
        Args:
            path: API path
            data: The data to send in the request body
            
        Returns:
            Response data as a dictionary
            
        Raises:
            ValueError: If the request fails or the API returns success=false
        """

        url = f"{self.higress_url}{path}"
        self.logger.info(f"POST request to: {url}, data: {data}")

        response = requests.post(url, json=data, auth=self.auth)
        return self._process_response(response, "POST", path)

    def put(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a PUT request to the Higress Console API.
        
        Args:
            path: API path
            data: The data to send in the request body
            
        Returns:
            Response data as a dictionary
            
        Raises:
            ValueError: If the request fails or the API returns success=false
        """
        url = f"{self.higress_url}{path}"
        self.logger.info(f"PUT request to: {url}, data: {data}")
        
        response = requests.put(url, json=data, auth=self.auth)
        return self._process_response(response, "PUT", path)
    
    def get_plugin(self, name: str, scope: str, resource_name: str = None) -> Dict[str, Any]:
        """Get detailed information about a specific Higress plugin.
        
        Args:
            name: The name of the plugin
            scope: The scope at which the plugin is applied. Must be one of: 
                  "global", "domain", "service", or "route"
            resource_name: The name of the resource (required for domain, service, route scopes)
            
        Returns:
            Plugin data as a dictionary
            
        Raises:
            ValueError: If resource_name is not provided for non-global scopes or scope is not specified
        """
        if scope != "global" and not resource_name:
            raise ValueError(f"resource_name is required for {scope} scope")
            
        paths = {
            "global": f"/v1/global/plugin-instances/{name}",
            "domain": f"/v1/domains/{resource_name}/plugin-instances/{name}",
            "service": f"/v1/services/{resource_name}/plugin-instances/{name}",
            "route": f"/v1/routes/{resource_name}/plugin-instances/{name}"
        }
        
        if scope not in paths:
            raise ValueError(f"Invalid scope: {scope}. Must be one of: global, domain, service, route")
            
        path = paths[scope]
        return self.get(path)
    
    def update_plugin(self, name: str, enabled: bool, configurations: Dict[str, Any], scope: str, resource_name: str = None) -> Dict[str, Any]:
        """Update a Higress plugin configuration.
        
        Args:
            name: The name of the plugin
            enabled: Whether the plugin is enabled
            configurations: The new configuration values to update
            scope: The scope at which the plugin is applied. Must be one of: 
                  "global", "domain", "service", or "route"
            resource_name: The name of the resource (required for domain, service, route scopes)
            
        Returns:
            Updated plugin data as a dictionary
            
        Raises:
            ValueError: If resource_name is not provided for non-global scopes or scope is not specified
        """

        # Get current plugin data avoid overwriting the old configurations
        data = self.get_plugin(name, scope, resource_name)

        # Update the configurations with the new values
        config = data["configurations"] or {}
        if configurations:
            config.update(configurations)
        
        data["configurations"] = config
        data["enabled"] = enabled

        # Determine the appropriate path based on scope
        paths = {
            "global": f"/v1/global/plugin-instances/{name}",
            "domain": f"/v1/domains/{resource_name}/plugin-instances/{name}",
            "service": f"/v1/services/{resource_name}/plugin-instances/{name}",
            "route": f"/v1/routes/{resource_name}/plugin-instances/{name}"
        }
        
        if scope not in paths:
            raise ValueError(f"Invalid scope: {scope}. Must be one of: global, domain, service, route")
            
        path = paths[scope]
        return self.put(path, data)
        
    def list_routes(self) -> List[Dict[str, Any]]:
        """
        Get a list of all routes.
        
        Returns:
            List of route data as dictionaries
            
        Raises:
            ValueError: If the request fails
        """
        path = "/v1/routes"
        return self.get(path)
        
    def get_route(self, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific route.
        
        Args:
            name: The name of the route
            
        Returns:
            Route data as a dictionary
            
        Raises:
            ValueError: If the route is not found or the request fails
        """
        path = f"/v1/routes/{name}"
        return self.get(path)
        
    def update_route(self, name: str, configurations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a route.
        
        Args:
            name: The name of the route (required)
            configurations: The route configuration dictionary

        Returns:
            The updated route configuration
            
        Raises:
            ValueError: If the request fails or required fields are missing
        """
        if not name:
            raise ValueError("Route name is required")

        # Get current route data avoid overwriting the old configurations
        route_config = self.get_route(name)
        if configurations:
            route_config.update(configurations)

        path = f"/v1/routes/{name}"
        return self.put(path, route_config)

    def add_route(self, configurations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a route.
        
        Args:
            configurations: The route configuration dictionary. Must contain at least:
                - name: The name of the route
                - path: The path configuration
                - services: The list of services for this route
                
        Returns:
            The updated route configuration
            
        Raises:
            ValueError: If the request fails or required fields are missing
        """
        if not configurations.get("name"):
            raise ValueError("Route name is required")
        if not configurations.get("path"):
            raise ValueError("Route path configuration is required")
        if not configurations.get("services"):
            raise ValueError("At least one service is required for the route")
            
        path = f"/v1/routes"
        return self.post(path, configurations)

    def list_service_sources(self) -> List[Dict[str, Any]]:
        """
        Get a list of all service sources from Higress.
        
        Returns:
            List of service sources data as dictionaries
            
        Raises:
            ValueError: If the request fails
        """
        path = "/v1/service-sources"
        return self.get(path)
        
    def add_service_source(self, configurations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new service source.
        
        Args:
            configurations: The service source configuration dictionary. Must contain at least:
                - name: The name of the service source
                - type: The type of the service source (static or dns)
                - domain: The domain name for the service source
                - port: The port number
                
        Returns:
            The created service source configuration
            
        Raises:
            ValueError: If the request fails or required fields are missing
        """
        if not configurations.get("name"):
            raise ValueError("Service source name is required")
        if not configurations.get("type"):
            raise ValueError("Service source type is required")
        if not configurations.get("domain"):
            raise ValueError("Service source domain is required")
        if not configurations.get("port"):
            raise ValueError("Service source port is required")
        
        source_type = configurations.get("type")
        if source_type == "dns" and not configurations.get("protocol"):
            raise ValueError("Protocol is required for DNS service sources")
                
        path = "/v1/service-sources"
        return self.post(path, configurations)
        
    def get_service_source(self, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific service source.
        
        Args:
            name: The name of the service source
            
        Returns:
            Service source data as a dictionary
            
        Raises:
            ValueError: If the service source is not found or the request fails
        """
        path = f"/v1/service-sources/{name}"
        return self.get(path)
        
    def update_service_source(self, name: str, configurations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a service source.
        
        Args:
            name: The name of the service source
            configurations: The service source configuration dictionary
                
        Returns:
            The updated service source configuration
            
        Raises:
            ValueError: If the request fails or required fields are missing
        """
        if not name:
            raise ValueError("Service source name is required")

        # Get current service source data avoid overwriting the old configurations
        service_source_config = self.get_service_source(name)
        if configurations:
            service_source_config.update(configurations)

        path = f"/v1/service-sources/{name}"
        return self.put(path, service_source_config)