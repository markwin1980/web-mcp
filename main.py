"""Web-MCP 服务器主入口 - 使用 FastMCP 实现。"""

from mcp.server.fastmcp import FastMCP

from web_reader import web_reader
from web_search import web_search

mcp = FastMCP(
    name="web-mcp",
    instructions="MCP 服务器，提供Web搜索，Web读取等功能",
)

# 将 web_search 函数注册为 MCP 工具
mcp.tool()(web_search)

# 将 web_reader 函数注册为 MCP 工具
mcp.tool()(web_reader)

if __name__ == "__main__":
    mcp.run()
