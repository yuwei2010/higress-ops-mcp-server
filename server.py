import logging

from fastmcp import FastMCP

from tools.plugins.common import CommonTools
from tools.plugins.request_block import RequestBlockTools
from tools.route import RouteTools
from tools.register import ToolsRegister
from tools.service_source import ServiceSourceTools
from utils.higress_client import HigressClient
from utils.params import parse_args, validate


class HigressMCPServer:
    def __init__(self, base_url=None, username=None, password=None):
        self.name = "higress-mcp-server"
        self.mcp = FastMCP(self.name)
        self.logger = logging.getLogger(self.name)
        
        # Initialize Higress client with provided credentials
        self.higress_client = HigressClient(
            logger=self.logger,
            base_url=base_url,
            username=username,
            password=password
        )

        # Initialize tools
        self._register_tools()   

    def _register_tools(self):
        """Register all MCP tools."""
        # Create a tools register
        register = ToolsRegister(self.logger, self.higress_client, self.mcp)
        
        # Define all tool classes to register
        tool_classes = [
            CommonTools,
            RequestBlockTools,
            RouteTools,
            ServiceSourceTools
        ]
        
        # Register all tools
        register.register_all_tools(tool_classes)

    def run(self):
        """Run the MCP server."""
        self.logger.info("Starting MCP server...")
        self.mcp.run()

def main():
    # Parse command line arguments
    args = parse_args("Higress MCP Server")
    
    # Get and validate credentials
    base_url, username, password = validate(
        base_url=args.base_url,
        username=args.username,
        password=args.password
    )
    
    # Create and run the server with provided configuration
    server = HigressMCPServer(
        base_url=base_url,
        username=username,
        password=password
    )
    server.run()

if __name__ == "__main__":
    import sys
    main()    