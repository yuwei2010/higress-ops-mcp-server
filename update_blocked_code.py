#!/usr/bin/env python3
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    """更新 request-block 插件的 blocked_code 为 429"""
    server_params = StdioServerParameters(
        command="python",
        args=["./server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            
            print("连接到 MCP 服务器成功!")
            
            # 获取可用工具
            response = await session.list_tools()
            print("可用工具:", [tool.name for tool in response.tools])
            
            # 获取当前插件配置
            print("获取当前 request-block 插件配置...")
            get_plugin_tool = next(tool for tool in response.tools if tool.name == "get_plugin")
            plugin_response = await session.invoke_tool(get_plugin_tool, {"name": "request-block"})
            print(f"当前配置: {plugin_response}")
            
            # 更新 blocked_code 为 429
            print("更新 blocked_code 为 429...")
            update_tool = next(tool for tool in response.tools if tool.name == "update_request_block_plugin")
            update_response = await session.invoke_tool(update_tool, {"blocked_code": 429})
            
            print(f"更新结果: {update_response}")
            print("更新完成!")

if __name__ == "__main__":
    asyncio.run(main())
