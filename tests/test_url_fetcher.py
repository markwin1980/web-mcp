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
async def test_url_fetcher_markdown_format(mcp_client):
    """测试返回 Markdown 格式。"""
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
    assert result_data["success"] is True
    assert result_data["url"] == TEST_URL
    assert "content" in result_data


@pytest.mark.asyncio
async def test_url_fetcher_text_format(mcp_client):
    """测试返回纯文本格式。"""
    result = await mcp_client.call_tool(
        "url_fetcher",
        {
            "url": TEST_URL,
            "return_format": "text",
            "timeout": 20,
        },
    )

    assert result, "工具未返回结果"
    assert len(result.content) > 0, "content 为空"

    content_item = result.content[0]
    content = content_item.text
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is True
    assert result_data["url"] == TEST_URL
    assert "content" in result_data
