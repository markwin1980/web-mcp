"""Web-Search 工具函数 - 提供 MCP 工具接口。"""

import json
import logging
from datetime import datetime
from pathlib import Path

from .client import BingSearchClient
from .config import BingSearchConfig
from .exceptions import BingSearchError

# 设置日志
logger = logging.getLogger("web_search")
logger.setLevel(logging.INFO)
if not logger.handlers:
    log_dir = Path("log")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"web_search_{datetime.now().strftime('%Y%m%d')}.log"
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)

# 全局 Bing 搜索客户端实例
_bing_client: BingSearchClient | None = None


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


def _get_bing_client() -> BingSearchClient:
    """获取或创建 Bing 搜索客户端实例。"""
    global _bing_client
    if _bing_client is None:
        config = BingSearchConfig.from_env()
        _bing_client = BingSearchClient(config)
    return _bing_client


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
    # 记录请求
    logger.info(f"REQUEST - query={query}, num_results={num_results}")

    try:
        # 参数验证
        if not (1 <= num_results <= 50):
            logger.info(f"RESPONSE - FAILED - query={query}, error=num_results 必须在 1-50 之间")
            return create_web_search_result(
                success=False,
                query=query,
                error="num_results 必须在 1-50 之间",
            )

        # 获取 Bing 搜索客户端并执行搜索
        client = _get_bing_client()
        results = await client.search(
            query=query,
            num_results=num_results,
        )

        # 确保每个结果都有 rank 字段
        for idx, result in enumerate(results):
            if "rank" not in result:
                result["rank"] = idx + 1

        logger.info(f"RESPONSE - SUCCESS - query={query}, total_results={len(results)}")
        return create_web_search_result(
            success=True,
            query=query,
            results=results,
            total_results=len(results),
        )

    except BingSearchError as e:
        logger.info(f"RESPONSE - FAILED - query={query}, error={e!s}")
        return create_web_search_result(
            success=False,
            query=query,
            error=f"{e!s}",
        )
    except Exception as e:
        error_msg = f"搜索错误：{e!s}"
        logger.info(f"RESPONSE - FAILED - query={query}, error={error_msg}")
        return create_web_search_result(
            success=False,
            query=query,
            error=error_msg,
        )
