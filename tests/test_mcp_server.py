"""MCP 服务器元数据和初始化测试。"""

from pathlib import Path

import pytest
from fastmcp import Client


# ============================================================================
# MCP 客户端相关
# ============================================================================


@pytest.fixture
async def mcp_client():
    """启动 MCP 服务器并返回客户端实例。"""
    server_path = Path("mcp_stdio.py")
    client = Client(server_path)

    try:
        async with client:
            yield client
    finally:
        pass


@pytest.mark.asyncio
async def test_server_initialization(mcp_client):
    """测试服务器初始化。"""
    # 客户端应该已经成功连接
    assert mcp_client is not None


@pytest.mark.asyncio
async def test_list_tools(mcp_client):
    """测试列出所有工具。"""
    tools = await mcp_client.list_tools()

    # 验证工具数量
    assert len(tools) == 3, f"期望 3 个工具，实际返回 {len(tools)} 个"

    # 获取工具名称
    tool_names = [tool.name for tool in tools]

    # 验证工具名称
    assert "web_search" in tool_names, "缺少 web_search 工具"
    assert "url_fetcher" in tool_names, "缺少 url_fetcher 工具"
    assert "web_dev" in tool_names, "缺少 web_dev 工具"


@pytest.mark.asyncio
async def test_tools_have_descriptions(mcp_client):
    """测试所有工具都有描述。"""
    tools = await mcp_client.list_tools()

    for tool in tools:
        assert tool.description, f"工具 {tool.name} 缺少描述"
        assert len(tool.description) > 0, f"工具 {tool.name} 的描述为空"


@pytest.mark.asyncio
async def test_tools_have_input_schema(mcp_client):
    """测试所有工具都有输入 schema。"""
    tools = await mcp_client.list_tools()

    for tool in tools:
        assert tool.inputSchema, f"工具 {tool.name} 缺少 inputSchema"

        input_schema = tool.inputSchema
        assert isinstance(input_schema, dict), f"工具 {tool.name} 的 inputSchema 不是字典"
        assert "properties" in input_schema, f"工具 {tool.name} 缺少 properties 定义"


@pytest.mark.asyncio
async def test_mcp_protocol_version(mcp_client):
    """测试 MCP 协议版本。"""
    # 初始化响应中应该包含协议版本
    init_result = await mcp_client.initialize()

    assert init_result.protocolVersion


@pytest.mark.asyncio
async def test_server_info(mcp_client):
    """测试服务器信息。"""
    init_result = await mcp_client.initialize()

    assert init_result.serverInfo
    server_info = init_result.serverInfo
    assert server_info.name == "web-mcp"
    assert server_info.version


@pytest.mark.asyncio
async def test_server_capabilities(mcp_client):
    """测试服务器能力声明。"""
    init_result = await mcp_client.initialize()

    assert init_result.capabilities

    capabilities = init_result.capabilities
    # 服务器应该支持工具
    assert capabilities.tools


@pytest.mark.asyncio
async def test_server_instructions(mcp_client):
    """测试服务器说明。"""
    init_result = await mcp_client.initialize()

    instructions = init_result.instructions
    assert isinstance(instructions, str)
    assert len(instructions) > 0
