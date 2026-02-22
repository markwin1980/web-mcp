"""Web-MCP 服务器入口 - 使用 stdio 传输。"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastmcp import FastMCP

from browser_service import initialize_global_browser, close_global_browser
from url_fetcher import url_fetcher
from web_search import web_search

# 加载 .env 文件中的环境变量
load_dotenv()


@asynccontextmanager
async def lifespan(_mcp: FastMCP):
    """管理 MCP 服务器的生命周期。"""
    # 启动时初始化浏览器
    await initialize_global_browser()
    yield
    # 退出时关闭浏览器
    await close_global_browser()


mcp = FastMCP(
    name="web-mcp",
    instructions="MCP 服务器，提供Web搜索，URL获取等功能",
    lifespan=lifespan,
)

# 将 web_search 函数注册为 MCP 工具
mcp.tool()(web_search)

# 将 url_fetcher 函数注册为 MCP 工具
mcp.tool()(url_fetcher)

if __name__ == "__main__":
    mcp.run(transport="stdio")
