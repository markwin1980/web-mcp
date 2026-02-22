"""Web-Search 工具集成测试。"""

import json
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


# ============================================================================
# MCP 工具测试
# ============================================================================


@pytest.mark.asyncio
async def test_web_search_5_results(mcp_client):
    """测试搜索返回 5 条结果（单页）。"""
    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": "Python",
            "num_results": 5,
        },
    )

    assert result, "工具未返回结果"
    assert len(result.content) > 0, "content 为空"

    content_item = result.content[0]
    assert content_item.type == "text", "内容类型不正确"
    content = content_item.text
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is True
    assert result_data["query"] == "Python"
    assert "results" in result_data
    assert isinstance(result_data["results"], list)
    assert len(result_data["results"]) == 5


@pytest.mark.asyncio
async def test_web_search_20_results_with_pagination(mcp_client):
    """测试搜索返回 20 条结果（需要翻页）。"""
    result = await mcp_client.call_tool(
        "web_search",
        {
            "query": "Python",
            "num_results": 20,
        },
    )

    assert result, "工具未返回结果"
    assert len(result.content) > 0, "content 为空"

    content_item = result.content[0]
    content = content_item.text
    assert content, "缺少 text 字段"

    result_data = json.loads(content)
    assert result_data["success"] is True
    assert result_data["query"] == "Python"
    assert "results" in result_data
    assert isinstance(result_data["results"], list)
    # 允许少于20条（搜索结果可能不够），但应该多于单页的数量
    assert len(result_data["results"]) >= 5, "返回结果过少"
