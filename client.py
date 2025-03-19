from os import getenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI
import asyncio

model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["./server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": "将 request-block 插件的请求被屏蔽时返回的 HTTP 状态码改成 500，其他配置保持不变"})
            print(agent_response)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())