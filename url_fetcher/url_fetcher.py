"""URL-Fetcher 工具函数 - 提供 MCP 工具接口。"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Literal

from url_fetcher.config import Config
from url_fetcher.fetcher import WebFetcher
from url_fetcher.models import URLFetcherInput
from url_fetcher.parser import HTMLParser

# 初始化 URL-Fetcher 工具所需的组件
config = Config()
fetcher = WebFetcher(config)
parser = HTMLParser()

# 设置日志
logger = logging.getLogger("url_fetcher")
logger.setLevel(logging.INFO)
if not logger.handlers:
    log_dir = Path("log")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"url_fetcher_{datetime.now().strftime('%Y%m%d')}.log"
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)


def create_url_fetcher_result(
        success: bool,
        url: str,
        title: str | None = None,
        summary: str | None = None,
        content: str | None = None,
        metadata: dict | None = None,
        error: str | None = None,
) -> str:
    """创建 URL 获取结果的 JSON 字符串。"""
    result = {
        "success": success,
        "url": url,
        "title": title,
        "summary": summary,
        "content": content,
        "metadata": metadata,
        "error": error,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


async def url_fetcher(
        url: str,
        return_format: Literal["markdown", "text"] = "markdown",
        retain_images: bool = True,
        timeout: int = 20,
        no_cache: bool = False,
) -> str:
    """读取网页并转换为 Markdown 或纯文本格式。"""
    # 记录请求
    logger.info(
        f"REQUEST - url={url}, return_format={return_format}, retain_images={retain_images}, timeout={timeout}, no_cache={no_cache}")

    try:
        if not (5 <= timeout <= 60):
            logger.info(f"RESPONSE - FAILED - url={url}, error=timeout 必须在 5-60 之间")
            return create_url_fetcher_result(False, url, error="timeout 必须在 5-60 之间")

        input_data = URLFetcherInput(
            url=url, return_format=return_format, retain_images=retain_images,
            timeout=timeout, no_cache=no_cache,
        )
        html = await fetcher.fetch(input_data.url, input_data.timeout, input_data.no_cache)
        result = await parser.parse(html, input_data.url, input_data)

        logger.info(f"RESPONSE - SUCCESS - url={url}, title={result.title}")
        return create_url_fetcher_result(True, result.url, result.title, result.summary, result.content, result.metadata)

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e!s}"
        logger.info(f"RESPONSE - FAILED - url={url}, error={error_msg}")
        return create_url_fetcher_result(False, url, error=error_msg)
