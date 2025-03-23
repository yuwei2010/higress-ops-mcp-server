import logging
from fastmcp import FastMCP
from tools.common import CommonTools
from tools.request_block import RequestBlockTools
from utils.higress_client import HigressClient

class HigressMCPServer:
    def __init__(self):
        self.name = "higress_mcp_server"
        self.mcp = FastMCP(self.name)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        
        self.higress_client = HigressClient(self.logger)

        # Initialize tools
        self._register_tools()

               

    def _register_tools(self):
        """Register all MCP tools."""
        # Initialize tool classes
        common_tools = CommonTools(self.logger, self.higress_client)
        request_block_tools = RequestBlockTools(self.logger, self.higress_client)
        
        # Register tools from each module
        common_tools.register_tools(self.mcp)
        request_block_tools.register_tools(self.mcp)

    def run(self):
        """Run the MCP server."""
        self.logger.info("Starting MCP server...")
        self.mcp.run()

def main():
    server = HigressMCPServer()
    server.run()

if __name__ == "__main__":
    main()    