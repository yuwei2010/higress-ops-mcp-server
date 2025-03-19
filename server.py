from typing import Dict
from mcp.server.fastmcp import FastMCP
import logging
import requests

MCP_SERVER_NAME = "higress-mcp-server"
cookies = {
    "_hi_sess": "OM6xeIuIyBQh1JJPwWrOrkpWAgq01LzhLmBHzxZ3M/c="
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(MCP_SERVER_NAME)

# Create FastMCP instance
mcp = FastMCP(MCP_SERVER_NAME)

@mcp.tool()
def get_plugin(name: str) -> Dict:
    logger.info(f"Get plugin: {name}")
    """Get detailed information about a specific Higress plugin"""
    try:
        response = requests.get(
            f"http://localhost:8001/v1/global/plugin-instances/{name}",
            cookies=cookies
        )
        if response.status_code == 404:
            raise ValueError(f"Plugin {name} not found")
        response.raise_for_status()
        plugin_data = response.json()
        logger.info(plugin_data)
        return plugin_data
    except requests.RequestException as e:
        raise ValueError(f"Failed to get plugin {name}: {str(e)}")

def validate_plugin_config(config: Dict) -> None:
    """Validate plugin configuration according to the schema requirements."""
    # Check if at least one of block_urls, block_headers, or block_bodies is provided
    required_fields = ['block_urls', 'block_headers', 'block_bodies']
    if not any(field in config for field in required_fields):
        raise ValueError(f"At least one of {', '.join(required_fields)} must be provided")
    
    # Validate array of string fields
    array_string_fields = [
        'block_urls', 'block_exact_urls', 'block_regexp_urls',
        'block_headers', 'block_bodies'
    ]
    for field in array_string_fields:
        if field in config:
            if not isinstance(config[field], list):
                raise ValueError(f"{field} must be an array")
            if not all(isinstance(item, str) for item in config[field]):
                raise ValueError(f"All items in {field} must be strings")
    
    # Validate blocked_code
    if 'blocked_code' in config:
        if not isinstance(config['blocked_code'], (int, float)):
            raise ValueError("blocked_code must be a number")
    
    # Validate blocked_message
    if 'blocked_message' in config:
        if not isinstance(config['blocked_message'], str):
            raise ValueError("blocked_message must be a string")
    
    # Validate case_sensitive
    if 'case_sensitive' in config:
        if not isinstance(config['case_sensitive'], bool):
            raise ValueError("case_sensitive must be a boolean")

@mcp.tool()
def set_plugin(name: str, configurations: Dict) -> Dict:
    logger.info(f"Set plugin: {name} with configurations: {configurations}")
    """Set configuration for a specific Higress plugin with validation"""
    try:
        validate_plugin_config(configurations)
        current_config = get_plugin(name)
        current_config["configurations"] = configurations
        
        # Send PUT request to update plugin configuration
        response = requests.put(
            f"http://localhost:8001/v1/global/plugin-instances/{name}",
            cookies=cookies,
            json=current_config,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except ValueError as e:
        raise
    except requests.RequestException as e:
        raise ValueError(f"Failed to set plugin {name}: {str(e)}")

def main():
    logger.info(f"Starting {MCP_SERVER_NAME}...")
    mcp.run()

if __name__ == "__main__":
    main()