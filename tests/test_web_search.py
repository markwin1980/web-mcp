"""Web-Search 工具集成测试。"""

import json

import pytest
from web_search import BingSearchClient, BingSearchConfig


@pytest.mark.asyncio
async def test_bing_search_basic():
    """测试基本的 Bing 搜索功能。"""
    config = BingSearchConfig()
    client = BingSearchClient(config)

    results = await client.search(
        query="Python programming",
        num_results=5,
    )

    assert len(results) == 5
    for result in results:
        assert "title" in result
        assert "url" in result
        assert "snippet" in result
        assert "rank" in result
        assert isinstance(result["rank"], int)
        assert result["rank"] >= 1


@pytest.mark.asyncio
async def test_bing_search_pagination():
    """测试翻页功能。"""
    config = BingSearchConfig()
    client = BingSearchClient(config)

    # 请求超过一页的结果（触发翻页）
    results = await client.search(
        query="Python",
        num_results=15,
    )

    assert len(results) == 15
    # 验证 rank 字段正确
    for idx, result in enumerate(results):
        assert result["rank"] == idx + 1


@pytest.mark.asyncio
async def test_bing_search_single_result():
    """测试只请求一个结果。"""
    config = BingSearchConfig()
    client = BingSearchClient(config)

    results = await client.search(
        query="test",
        num_results=1,
    )

    assert len(results) == 1
    assert results[0]["rank"] == 1


@pytest.mark.asyncio
async def test_bing_search_empty_query():
    """测试空查询字符串。"""
    config = BingSearchConfig()
    client = BingSearchClient(config)

    # 空查询可能返回一些结果或空列表
    results = await client.search(
        query="",
        num_results=5,
    )

    # 至少不会抛出异常
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_bing_search_chinese_query():
    """测试中文查询。"""
    config = BingSearchConfig()
    client = BingSearchClient(config)

    results = await client.search(
        query="Python 编程",
        num_results=5,
    )

    assert len(results) == 5


@pytest.mark.asyncio
async def test_bing_search_result_format():
    """测试返回结果的数据格式。"""
    config = BingSearchConfig()
    client = BingSearchClient(config)

    results = await client.search(
        query="test",
        num_results=3,
    )

    assert len(results) == 3

    for result in results:
        # 验证必需字段存在
        assert "title" in result
        assert "url" in result
        assert "snippet" in result
        assert "rank" in result

        # 验证字段类型
        assert isinstance(result["title"], str)
        assert isinstance(result["url"], str)
        assert isinstance(result["snippet"], str)
        assert isinstance(result["rank"], int)

        # 验证字段非空
        assert result["title"]
        assert result["url"]
        # snippet 可能为空


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
            "query": "Python",
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
