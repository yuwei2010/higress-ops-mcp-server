import logging
import requests
from typing import Dict, List, Any

class HigressClient:
    """Client for interacting with Higress API."""
    
    def __init__(self, logger: logging.Logger):
        """Initialize the Higress client.
        
        Args:
            logger: Logger instance for logging requests and responses
        """
        self.logger = logger
        self.base_url = "http://localhost:8001"
        self.cookies = {
            "_hi_sess": "OM6xeIuIyBQh1JJPwWrOrkpWAgq01LzhLmBHzxZ3M/c="
        }

    def get(self, path: str) -> Dict[str, Any]:
        """Make a GET request to the Higress API.
        
        Args:
            path: API path (without base URL)
            
        Returns:
            Response data as a dictionary
            
        Raises:
            ValueError: If the request fails
        """
        url = f"{self.base_url}{path}"
        self.logger.info(f"GET request to: {url}")
        
        try:
            response = requests.get(url, cookies=self.cookies)
            response.raise_for_status()
            return response.json()["data"]
            
        except requests.RequestException as e:
            self.logger.error(f"GET request failed for {path}: {str(e)}")
            raise ValueError(f"Request failed: {str(e)}")
    
    def put(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a PUT request to the Higress API.
        
        Args:
            path: API path (without base URL)
            data: The data to send in the request body
            
        Returns:
            Response data as a dictionary
            
        Raises:
            ValueError: If the request fails
        """
        url = f"{self.base_url}{path}"
        self.logger.info(f"PUT request to: {url}")
        
        # 生成等效的curl命令用于手动测试
        import json
        cookie_str = '; '.join([f"{k}={v}" for k, v in self.cookies.items()])
        curl_cmd = f'''curl -X PUT \
  '{url}' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: {cookie_str}' \
  -d '{json.dumps(data)}' '''
        self.logger.info(f"Equivalent curl command:\n{curl_cmd}")
        
        try:
            response = requests.put(
                url,
                cookies=self.cookies,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            self.logger.info(f"PUT request successful: {path}")
            return response_data
            
        except requests.RequestException as e:
            self.logger.error(f"PUT request failed for {path}: {str(e)}")
            raise ValueError(f"Request failed: {str(e)}")
    
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
            Updated plugin data
            
        Raises:
            ValueError: If resource_name is not provided for non-global scopes or scope is not specified
        """
        # Get current plugin data using the appropriate scope
        data = self.get_plugin(name, scope, resource_name)
        config = data["configurations"]
        
        # Update configuration with new values
        for key, value in configurations.items():
            config[key] = value
        
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
        Get a list of all routes from Higress.
        
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
