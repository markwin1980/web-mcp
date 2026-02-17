"""Web-Search 工具集成测试。"""

import json

import pytest


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

    # 验证输入 schema
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
            "query": "测试搜索",
            "num_results": 5,
        },
    )

    # 验证返回内容 - FastMCP 返回格式: {content: [{type, text}], ...}
    assert result, "工具未返回结果"
    assert "content" in result, "缺少 content 字段"
    content_list = result["content"]
    assert len(content_list) > 0, "content 为空"

    # 获取第一个文本内容
    content_item = content_list[0]
    assert content_item.get("type") == "text", "内容类型不正确"
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    # 解析 JSON 结果
    result_data = json.loads(content)
    assert result_data["success"] is True
    assert result_data["query"] == "测试搜索"
    assert "results" in result_data
    assert isinstance(result_data["results"], list)


@pytest.mark.asyncio
async def test_call_web_search_invalid_params(mcp_client):
    """测试使用无效参数调用 web_search。"""
    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": "测试",
            "num_results": 51,  # 超出范围（最大50）
        },
    )

    # 应该返回错误
    assert result, "工具未返回结果"
    assert "content" in result, "缺少 content 字段"
    content_list = result["content"]
    assert len(content_list) > 0, "content 为空"

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
    assert "content" in result, "缺少 content 字段"
    content_list = result["content"]
    assert len(content_list) > 0, "content 为空"

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is True
    # 默认 num_results 是 10
    assert len(result_data["results"]) <= 10


@pytest.mark.asyncio
async def test_web_search_empty_query(mcp_client):
    """测试空查询字符串。"""
    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": "",
        },
    )

    assert result, "工具未返回结果"
    assert "content" in result, "缺少 content 字段"
    content_list = result["content"]
    assert len(content_list) > 0, "content 为空"

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    # 空查询应该也能返回成功，只是结果可能为空
    assert result_data["success"] is True


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
    assert "content" in result, "缺少 content 字段"
    content_list = result["content"]
    assert len(content_list) > 0, "content 为空"

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is True
    assert result_data["total_results"] == 1
    assert len(result_data["results"]) == 1
