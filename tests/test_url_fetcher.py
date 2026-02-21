"""URL-Fetcher 工具集成测试。"""

import json
import time

import pytest

# 测试用的 URL，可以修改为其他网站用于测试
TEST_URL = "https://www.cnblogs.com/"


@pytest.mark.asyncio
async def test_url_fetcher_tool_schema(mcp_client):
    """测试 url_fetcher 工具的元数据。"""
    tools = await mcp_client.list_tools()
    url_fetcher_tool = next(
        (tool for tool in tools if tool["name"] == "url_fetcher"), None
    )

    assert url_fetcher_tool is not None, "找不到 url_fetcher 工具"
    assert url_fetcher_tool["name"] == "url_fetcher"
    assert url_fetcher_tool.get("description"), "缺少工具描述"

    input_schema = url_fetcher_tool.get("inputSchema", {})
    assert input_schema, "缺少输入 schema"
    assert "properties" in input_schema, "缺少 properties 定义"

    properties = input_schema["properties"]
    assert "url" in properties, "缺少 url 参数"
    assert "return_format" in properties, "缺少 return_format 参数"
    assert "retain_images" in properties, "缺少 retain_images 参数"
    assert "timeout" in properties, "缺少 timeout 参数"
    assert "no_cache" in properties, "缺少 no_cache 参数"


@pytest.mark.asyncio
async def test_call_url_fetcher_with_public_site(mcp_client):
    """测试调用 url_fetcher 工具（使用公开网站）。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": TEST_URL,
            "return_format": "markdown",
            "retain_images": False,
            "timeout": 20,
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
    assert "url" in result_data
    assert result_data["url"] == TEST_URL


@pytest.mark.asyncio
async def test_call_url_fetcher_invalid_url(mcp_client):
    """测试使用无效 URL 调用 url_fetcher。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": "not-a-valid-url",
            "return_format": "markdown",
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
    assert result_data["success"] is False
    assert "error" in result_data


@pytest.mark.asyncio
async def test_url_fetcher_invalid_timeout(mcp_client):
    """测试无效的超时参数。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": TEST_URL,
            "timeout": 100,
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
    assert result_data["success"] is False
    assert "error" in result_data


@pytest.mark.asyncio
async def test_url_fetcher_text_format(mcp_client):
    """测试返回纯文本格式。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": TEST_URL,
            "return_format": "text",
            "retain_images": False,
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
    assert "url" in result_data
    # text 格式不应该包含 markdown 标题
    assert "content" in result_data


@pytest.mark.asyncio
async def test_url_fetcher_markdown_format(mcp_client):
    """测试返回 Markdown 格式。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": TEST_URL,
            "return_format": "markdown",
            "retain_images": False,
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
    assert "url" in result_data
    assert "content" in result_data


@pytest.mark.asyncio
async def test_url_fetcher_with_images(mcp_client):
    """测试保留图片选项。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": TEST_URL,
            "return_format": "markdown",
            "retain_images": True,
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
    assert "url" in result_data


@pytest.mark.asyncio
async def test_url_fetcher_cache_functionality(mcp_client):
    """测试缓存功能（第二次请求应该更快）。"""
    url = TEST_URL

    # 第一次请求
    start = time.time()
    result1 = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": url,
            "return_format": "markdown",
        },
    )
    first_duration = time.time() - start

    assert result1, "第一次请求失败"
    assert "content" in result1
    content1 = json.loads(result1["content"][0]["text"])
    assert content1["success"] is True

    # 第二次请求（应该使用缓存）
    start = time.time()
    result2 = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": url,
            "return_format": "markdown",
        },
    )
    second_duration = time.time() - start

    assert result2, "第二次请求失败"
    assert "content" in result2
    content2 = json.loads(result2["content"][0]["text"])
    assert content2["success"] is True

    # 验证内容一致
    assert content1["content"] == content2["content"]


@pytest.mark.asyncio
async def test_url_fetcher_no_cache(mcp_client):
    """测试禁用缓存选项。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": TEST_URL,
            "no_cache": True,
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
    assert "url" in result_data


@pytest.mark.asyncio
async def test_url_fetcher_default_params(mcp_client):
    """测试使用默认参数。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": TEST_URL,
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
    assert "url" in result_data
    assert result_data["url"] == TEST_URL


@pytest.mark.asyncio
async def test_url_fetcher_content_structure(mcp_client):
    """测试返回内容的结构完整性。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": TEST_URL,
            "return_format": "markdown",
        },
    )

    assert result, "工具未返回结果"
    assert "content" in result
    content = json.loads(result["content"][0]["text"])

    # 验证基本字段存在
    assert "success" in content
    assert "url" in content
    assert "content" in content

    # 成功时应该有这些字段
    if content["success"]:
        assert "title" in content
        assert "summary" in content or "content" in content
