"""URL-Fetcher 工具集成测试。"""

import json
from pathlib import Path

import pytest
from fastmcp import Client

# 测试用的 URL，可以修改为其他网站用于测试
TEST_URL = "https://www.cnblogs.com/"


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


# ============================================================================
# MCP 工具测试
# ============================================================================


@pytest.mark.asyncio
async def test_call_url_fetcher_with_public_site(mcp_client):
    """测试调用 url_fetcher 工具（使用公开网站）。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": TEST_URL,
            "return_format": "markdown",
            "timeout": 20,
        },
    )

    assert result, "工具未返回结果"
    assert len(result.content) > 0, "content 为空"

    content_item = result.content[0]
    content = content_item.text
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
    assert len(result.content) > 0, "content 为空"

    content_item = result.content[0]
    content = content_item.text
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
    assert len(result.content) > 0, "content 为空"

    content_item = result.content[0]
    content = content_item.text
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
        },
    )

    assert result, "工具未返回结果"
    assert len(result.content) > 0, "content 为空"

    content_item = result.content[0]
    content = content_item.text
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
        },
    )

    assert result, "工具未返回结果"
    assert len(result.content) > 0, "content 为空"

    content_item = result.content[0]
    content = content_item.text
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert "url" in result_data
    assert "content" in result_data


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
    assert len(result.content) > 0, "content 为空"

    content_item = result.content[0]
    content = content_item.text
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
    content = json.loads(result.content[0].text)

    # 验证基本字段存在
    assert "success" in content
    assert "url" in content
    assert "content" in content

    # 成功时应该有这些字段
    if content["success"]:
        assert "title" in content
        assert "summary" in content or "content" in content
