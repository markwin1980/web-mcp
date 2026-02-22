"""Web-Search 工具函数 - 提供 MCP 工具接口。"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from browser_service import get_global_browser_service
from web_search.bing_client import BingClient
from web_search.config import BingSearchConfig
from web_search.exceptions import BingSearchError

logger = logging.getLogger("web_search")
logger.setLevel(logging.INFO)
if not logger.handlers:
    try:
        log_dir = Path("log")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"web_search_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    except (OSError, PermissionError):
        logger.addHandler(logging.NullHandler())


def create_web_search_result(
        success: bool,
        query: str,
        results: list[dict[str, Any]] | None = None,
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
) -> str:
    """执行 Web 搜索并返回结果。

    使用 Playwright 访问 Bing.com 进行搜索。

    Args:
        query: 搜索关键词
        num_results: 返回结果数量，范围 1-50，默认为 10

    Returns:
        JSON 格式的字符串，包含 success、query、results、total_results 和 error 字段
    """
    search_config = BingSearchConfig.from_env()

    query = query.strip()

    if not query:
        logger.warning("搜索请求失败：query 为空")
        return create_web_search_result(
            success=False,
            query="",
            error="搜索关键词不能为空"
        )

    if len(query) > 500:
        logger.warning(f"搜索请求失败：query 长度过长 ({len(query)} 字符)")
        return create_web_search_result(
            success=False,
            query=query[:50] + "...",
            error="搜索关键词过长，最多500个字符"
        )

    query_cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', query)
    if query_cleaned != query:
        logger.warning(f"Query 包含控制字符，已清理")
        query = query_cleaned

    logger.info(f"REQUEST - query={query}, num_results={num_results}")

    try:
        if not (1 <= num_results <= search_config.max_results):
            logger.error(f"搜索请求失败：num_results 超出范围 ({num_results})")
            return create_web_search_result(
                success=False,
                query=query,
                error=f"num_results 必须在 1-{search_config.max_results} 之间",
            )

        browser_service = await get_global_browser_service()
        client = BingClient(
            search_config=search_config,
            browser_service=browser_service
        )

        results = await client.search(
            query=query,
            num_results=num_results,
        )

        logger.info(f"搜索成功：query='{query}', 返回 {len(results)} 条结果")
        return create_web_search_result(
            success=True,
            query=query,
            results=results,
            total_results=len(results),
        )

    except BingSearchError as e:
        logger.error(f"搜索失败：query='{query}', 错误: {e!s}")
        return create_web_search_result(
            success=False,
            query=query,
            error=f"{e!s}",
        )
    except Exception as e:
        error_msg = f"搜索错误：{e!s}"
        logger.error(f"搜索异常：query='{query}', 错误: {error_msg}")
        return create_web_search_result(
            success=False,
            query=query,
            error=error_msg,
        )
