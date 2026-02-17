"""Web-Reader 工具集成测试。"""

import json

import pytest


@pytest.mark.asyncio
async def test_web_reader_tool_schema(mcp_client):
    """测试 web_reader 工具的元数据。"""
    tools = await mcp_client.list_tools()
    web_reader_tool = next(
        (tool for tool in tools if tool["name"] == "web_reader"), None
    )

    assert web_reader_tool is not None, "找不到 web_reader 工具"
    assert web_reader_tool["name"] == "web_reader"
    assert web_reader_tool.get("description"), "缺少工具描述"

    # 验证输入 schema
    input_schema = web_reader_tool.get("inputSchema", {})
    assert input_schema, "缺少输入 schema"
    assert "properties" in input_schema, "缺少 properties 定义"

    properties = input_schema["properties"]
    assert "url" in properties, "缺少 url 参数"
    assert "return_format" in properties, "缺少 return_format 参数"
    assert "retain_images" in properties, "缺少 retain_images 参数"
    assert "timeout" in properties, "缺少 timeout 参数"
    assert "no_cache" in properties, "缺少 no_cache 参数"


@pytest.mark.asyncio
async def test_call_web_reader_with_public_site(mcp_client):
    """测试调用 web_reader 工具（使用公开网站）。"""
    result = await mcp_client.call_tool(
        "web_reader",
        {
            "url": "https://example.com",
            "return_format": "markdown",
            "retain_images": False,
            "timeout": 20,
        },
    )

    # 验证返回内容
    assert result, "工具未返回结果"
    assert "content" in result, "缺少 content 字段"
    content_list = result["content"]
    assert len(content_list) > 0, "content 为空"

    content_item = content_list[0]
    content = content_item.get("text")
    assert content, "缺少 text 字段"

    # 解析 JSON 结果
    result_data = json.loads(content)
    # 验证基本结构
    assert "url" in result_data
    assert result_data["url"] == "https://example.com"


@pytest.mark.asyncio
async def test_call_web_reader_invalid_url(mcp_client):
    """测试使用无效 URL 调用 web_reader。"""
    result = await mcp_client.call_tool(
        "web_reader",
        {
            "url": "not-a-valid-url",
            "return_format": "markdown",
        },
    )

    # 验证返回错误
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
async def test_web_reader_invalid_timeout(mcp_client):
    """测试无效的超时参数。"""
    result = await mcp_client.call_tool(
        "web_reader",
        {
            "url": "https://example.com",
            "timeout": 100,  # 超出范围
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
async def test_web_reader_text_format(mcp_client):
    """测试返回纯文本格式。"""
    result = await mcp_client.call_tool(
        "web_reader",
        {
            "url": "https://example.com",
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
    # 只验证基本结构，内容可能因为网络原因变化
    assert "url" in result_data


@pytest.mark.asyncio
async def test_web_reader_with_images(mcp_client):
    """测试保留图片选项。"""
    result = await mcp_client.call_tool(
        "web_reader",
        {
            "url": "https://example.com",
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
async def test_web_reader_no_cache(mcp_client):
    """测试禁用缓存选项。"""
    result = await mcp_client.call_tool(
        "web_reader",
        {
            "url": "https://example.com",
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
async def test_web_reader_default_params(mcp_client):
    """测试使用默认参数。"""
    result = await mcp_client.call_tool(
        "web_reader",
        {
            "url": "https://example.com",
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
    # 验证默认值被应用
    assert result_data["url"] == "https://example.com"
