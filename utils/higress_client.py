import logging
import requests
from typing import Dict, Any

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
            response = requests.get(
                url,
                cookies=self.cookies
            )
            
            if response.status_code == 404:
                raise ValueError(f"Resource not found: {path}")
                
            response.raise_for_status()
            data = response.json()
            
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Response data: {data}")
                
            return data
            
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
    
    def get_plugin(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a specific Higress plugin.
        
        Args:
            name: The name of the plugin
            
        Returns:
            Plugin data as a dictionary
        """
        path = f"/v1/global/plugin-instances/{name}"
        return self.get(path)
    
    def update_plugin(self, name: str, configurations: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Higress plugin configuration.
        
        Args:
            name: The name of the plugin
            configurations: The new configuration values to update
            
        Returns:
            Updated plugin data
        """
        data = self.get_plugin(name)["data"]
        config = data["configurations"]
        for key, value in configurations.items():
            config[key] = value
        
        data["configurations"] = config

        path = f"/v1/global/plugin-instances/{name}"
        return self.put(path, data)