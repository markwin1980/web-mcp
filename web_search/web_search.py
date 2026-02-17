"""Web-Search 工具函数 - 提供 MCP 工具接口。"""

import json


def create_web_search_result(
    success: bool,
    query: str,
    results: list | None = None,
    total_results: int | None = None,
    error: str | None = None,
) -> str:
    """创建 Web 搜索结果的 JSON 字符串。"""
    result = {
        "success": success,
        "query": query,
        "results": results,
        "total_results": total_results,
        "error": error,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


async def web_search(
    query: str,
    num_results: int = 10,
    language: str = "zh-cn",
) -> str:
    """执行 Web 搜索并返回结果。

    注意：当前使用模拟数据，实际使用时需要集成真实的搜索 API（如 Google、Bing 或 DuckDuckGo）。

    Args:
        query: 搜索关键词
        num_results: 返回结果数量，范围 1-100，默认为 10
        language: 搜索语言，默认为 zh-cn

    Returns:
        JSON 格式的字符串，包含 success、query、results、total_results 和 error 字段
    """
    try:
        # 参数验证
        if not (1 <= num_results <= 100):
            return create_web_search_result(
                success=False,
                query=query,
                error="num_results 必须在 1-100 之间",
            )

        # TODO: 集成真实的搜索 API
        # 当前返回模拟数据
        mock_results = [
            {
                "title": f"模拟搜索结果 {i + 1} - {query}",
                "url": f"https://example.com/result-{i + 1}",
                "snippet": f"这是关于 {query} 的模拟搜索结果描述。在实际集成后，这里将显示真实的搜索摘要。",
                "rank": i + 1,
            }
            for i in range(min(num_results, 5))  # 模拟最多 5 个结果
        ]

        return create_web_search_result(
            success=True,
            query=query,
            results=mock_results,
            total_results=len(mock_results),
        )

    except Exception as e:
        return create_web_search_result(
            success=False,
            query=query,
            error=f"搜索错误：{e!s}",
        )
