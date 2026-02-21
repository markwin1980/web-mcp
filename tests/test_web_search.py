"""Web-Search 工具集成测试。"""

import json

import pytest


# ============================================================================
# MCP 工具测试
# ============================================================================


@pytest.mark.asyncio
async def test_web_search_tool_schema(mcp_client):
    """测试 web_search 工具的元数据。"""
    tools = await mcp_client.list_tools()
    web_search_tool = next(
        (tool for tool in tools if tool["name"] == "web_search"), None
    )

    assert web_search_tool is not None, "找不到 web_search 工具"
    assert web_search_tool["name"] == "web_search"
    assert web_search_tool.get("description"), "缺少工具描述"

    input_schema = web_search_tool.get("inputSchema", {})
    assert input_schema, "缺少输入 schema"
    assert "properties" in input_schema, "缺少 properties 定义"

    properties = input_schema["properties"]
    assert "query" in properties, "缺少 query 参数"
    assert "num_results" in properties, "缺少 num_results 参数"


@pytest.mark.asyncio
async def test_call_web_search(mcp_client):
    """测试调用 web_search 工具。"""
    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": "Python",
            "num_results": 5,
        },
    )

    assert result, "工具未返回结果"
    assert "content" in result, "缺少 content 字段"
    content_list = result["content"]
    assert len(content_list) > 0, "content 为空"

    content_item = content_list[0]
    assert content_item.get("type") == "text", "内容类型不正确"
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is True
    assert result_data["query"] == "Python"
    assert "results" in result_data
    assert isinstance(result_data["results"], list)
    assert len(result_data["results"]) == 5


@pytest.mark.asyncio
async def test_call_web_search_invalid_params(mcp_client):
    """测试使用无效参数调用 web_search。"""
    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": "test",
            "num_results": 51,
        },
    )

    assert result, "工具未返回结果"
    assert "content" in result
    content_list = result["content"]
    assert len(content_list) > 0

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is False
    assert "error" in result_data


@pytest.mark.asyncio
async def test_web_search_default_params(mcp_client):
    """测试使用默认参数调用 web_search。"""
    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": "默认参数测试",
        },
    )

    assert result, "工具未返回结果"
    assert "content" in result
    content_list = result["content"]
    assert len(content_list) > 0

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is True
    assert len(result_data["results"]) <= 10


@pytest.mark.asyncio
async def test_web_search_minimum_results(mcp_client):
    """测试返回最小数量结果。"""
    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": "最小结果测试",
            "num_results": 1,
        },
    )

    assert result, "工具未返回结果"
    assert "content" in result
    content_list = result["content"]
    assert len(content_list) > 0

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is True
    assert result_data["total_results"] == 1
    assert len(result_data["results"]) == 1


@pytest.mark.asyncio
async def test_web_search_empty_query(mcp_client):
    """测试空查询或仅包含空格的查询。"""
    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": "   ",
        },
    )

    assert result, "工具未返回结果"
    assert "content" in result
    content_list = result["content"]
    assert len(content_list) > 0

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is False
    assert "不能为空" in result_data["error"]


@pytest.mark.asyncio
async def test_web_search_too_long_query(mcp_client):
    """测试超长查询字符串。"""
    long_query = "a" * 1000

    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": long_query,
        },
    )

    assert result, "工具未返回结果"
    assert "content" in result
    content_list = result["content"]
    assert len(content_list) > 0

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is False
    assert "过长" in result_data["error"]
    assert len(result_data["query"]) <= 53


@pytest.mark.asyncio
async def test_web_search_query_with_control_chars(mcp_client):
    """测试包含控制字符的查询。"""
    injection_query = "搜索\x1b[2J\x1b[H内容"

    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": injection_query,
            "num_results": 1,
        },
    )

    assert result, "工具未返回结果"
    assert "content" in result
    content_list = result["content"]
    assert len(content_list) > 0

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is True
    assert "\x1b" not in result_data["query"]


@pytest.mark.asyncio
async def test_web_search_query_at_max_length(mcp_client):
    """测试刚好500字符的查询（边界测试）。"""
    max_query = "a" * 500

    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": max_query,
            "num_results": 1,
        },
    )

    assert result, "工具未返回结果"
    assert "content" in result
    content_list = result["content"]
    assert len(content_list) > 0

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is True
    assert result_data["query"] == max_query
