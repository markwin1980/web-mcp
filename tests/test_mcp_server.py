"""MCP 服务器元数据和初始化测试。"""

import asyncio

import pytest


@pytest.mark.asyncio
async def test_server_initialization(mcp_client):
    """测试服务器初始化。"""
    # 服务器应该已经成功启动并初始化
    assert mcp_client.process.poll() is None, "服务器进程未运行"


@pytest.mark.asyncio
async def test_list_tools(mcp_client):
    """测试列出所有工具。"""
    tools = await mcp_client.list_tools()

    # 验证工具数量
    assert len(tools) == 2, f"期望 2 个工具，实际返回 {len(tools)} 个"

    # 获取工具名称
    tool_names = [tool["name"] for tool in tools]

    # 验证工具名称
    assert "web_search" in tool_names, "缺少 web_search 工具"
    assert "url_fetcher" in tool_names, "缺少 url_fetcher 工具"


@pytest.mark.asyncio
async def test_tools_have_descriptions(mcp_client):
    """测试所有工具都有描述。"""
    tools = await mcp_client.list_tools()

    for tool in tools:
        assert tool.get("description"), f"工具 {tool['name']} 缺少描述"
        assert len(tool["description"]) > 0, f"工具 {tool['name']} 的描述为空"


@pytest.mark.asyncio
async def test_tools_have_input_schema(mcp_client):
    """测试所有工具都有输入 schema。"""
    tools = await mcp_client.list_tools()

    for tool in tools:
        assert "inputSchema" in tool, f"工具 {tool['name']} 缺少 inputSchema"

        input_schema = tool["inputSchema"]
        assert isinstance(input_schema, dict), f"工具 {tool['name']} 的 inputSchema 不是字典"
        assert "properties" in input_schema, f"工具 {tool['name']} 缺少 properties 定义"


@pytest.mark.asyncio
async def test_concurrent_tool_calls(mcp_client):
    """测试并发调用工具。"""
    # 同时调用多个工具
    tasks = [
        mcp_client.call_tool(
            "web_search",
            {"query": f"搜索 {i}", "num_results": 2},
        )
        for i in range(3)
    ]

    results = await asyncio.gather(*tasks)

    # 验证所有调用都成功
    assert len(results) == 3
    for i, result in enumerate(results):
        assert result, f"任务 {i} 未返回结果"
        assert "content" in result, f"任务 {i} 缺少 content 字段"
        content_list = result["content"]
        assert len(content_list) > 0, f"任务 {i} content 为空"

        content_item = content_list[0]
        content = content_item.get("text")
        assert content, f"任务 {i} 缺少 text 字段"

        import json

        result_data = json.loads(content)
        assert result_data["success"] is True, f"任务 {i} 失败"


@pytest.mark.asyncio
async def test_mcp_protocol_version(mcp_client):
    """测试 MCP 协议版本。"""
    # 初始化响应中应该包含协议版本
    init_response = await mcp_client.initialize()

    assert "result" in init_response
    result = init_response["result"]
    assert "protocolVersion" in result
    assert result["protocolVersion"] == "2024-11-05"


@pytest.mark.asyncio
async def test_server_info(mcp_client):
    """测试服务器信息。"""
    init_response = await mcp_client.initialize()

    assert "result" in init_response
    result = init_response["result"]
    assert "serverInfo" in result

    server_info = result["serverInfo"]
    assert "name" in server_info
    assert server_info["name"] == "web-mcp"
    assert "version" in server_info


@pytest.mark.asyncio
async def test_server_capabilities(mcp_client):
    """测试服务器能力声明。"""
    init_response = await mcp_client.initialize()

    assert "result" in init_response
    result = init_response["result"]
    assert "capabilities" in result

    capabilities = result["capabilities"]
    assert "tools" in capabilities
    # 服务器应该支持工具
    assert isinstance(capabilities["tools"], dict)


@pytest.mark.asyncio
async def test_server_instructions(mcp_client):
    """测试服务器说明。"""
    init_response = await mcp_client.initialize()

    assert "result" in init_response
    result = init_response["result"]
    assert "instructions" in result

    instructions = result["instructions"]
    assert isinstance(instructions, str)
    assert len(instructions) > 0
