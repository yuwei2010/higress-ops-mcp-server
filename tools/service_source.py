from typing import Dict, List, Any
from fastmcp import FastMCP

class ServiceSourceTools:
    def register_tools(self, mcp: FastMCP):
        @mcp.tool()
        async def list_service_sources() -> List[Dict]:
            """
            List all available service sources.
            
            Returns:
                List of service sources data as dictionaries
            
            Raises:
                ValueError: If the request fails
            """
            return self.higress_client.list_service_sources()
            
        @mcp.tool()
        async def add_service_source(configurations: Dict[str, Any]) -> Dict:
            """
            Add a new service source.
            
            Args:
                configurations: Dict[str, Any] containing the following keys:
                    - name (required): The name of the service source
                    - type (required): The type of the service source, must be one of:
                      * static: For static services with keys:
                        - domain: The domain name (e.g. "127.0.0.1:8001")
                        - port: The port number (e.g. 80)
                      * dns: For DNS-based services with keys:
                        - domain: The domain name (e.g. "dashscope.aliyuncs.com")
                        - port: The port number (e.g. 443)
                        - protocol: The protocol (e.g. "https")
                        - sni (optional): Server Name Indication for TLS (e.g. "dashscope.aliyuncs.com")
            
            Returns:
                The created service source configuration
                
            Raises:
                ValueError: If the request fails or required fields are missing
            """
            return self.higress_client.add_service_source(configurations)
            
        @mcp.tool()
        async def get_service_source(name: str) -> Dict:
            """
            Get detailed information about a specific service source.
            
            Args:
                name: The name of the service source
                
            Returns:
                Service source data as a dictionary
                
            Raises:
                ValueError: If the service source is not found or the request fails
            """
            return self.higress_client.get_service_source(name)
            
        @mcp.tool()
        async def update_service_source(name: str, configurations: Dict[str, Any]) -> Dict:
            """
            Update a service source.
            
            Args:
                name: The name of the service source
                configurations: Dict[str, Any] containing the configuration to update
                    
            Returns:
                The updated service source configuration
                
            Raises:
                ValueError: If the request fails or required fields are missing
            """
            return self.higress_client.update_service_source(name, configurations)         
        