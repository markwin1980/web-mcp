"""URL-Fetcher 工具函数 - 提供 MCP 工具接口。"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Literal

from browser_service import get_global_browser_service
from url_fetcher.config import Config
from url_fetcher.exceptions import FetchError, URLValidationError
from url_fetcher.html_parser import HTMLParser
from url_fetcher.web_client import WebClient

config = Config()

logger = logging.getLogger("url_fetcher")
logger.setLevel(logging.INFO)
if not logger.handlers:
    try:
        log_dir = Path("log")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"url_fetcher_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    except (OSError, PermissionError):
        logger.addHandler(logging.NullHandler())


def create_url_fetcher_result(
        success: bool,
        url: str,
        title: str | None = None,
        summary: str | None = None,
        content: str | None = None,
        metadata: dict | None = None,
        error: str | None = None,
) -> str:
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
        timeout: int = config.default_timeout,
        no_cache: bool = False,
) -> str:
    """读取网页并转换为 Markdown 或纯文本格式。"""
    logger.info(
        f"REQUEST - url={url}, return_format={return_format}, retain_images={retain_images}, timeout={timeout}, no_cache={no_cache}")

    try:
        url = url.strip()

        if not url:
            logger.warning("URL 获取请求失败：url 为空")
            return create_url_fetcher_result(
                success=False,
                url="",
                error="URL 不能为空"
            )

        if not url.startswith(("http://", "https://")):
            logger.warning(f"URL 获取请求失败：无效的 URL 协议 {url}")
            return create_url_fetcher_result(
                success=False,
                url=url,
                error="URL 必须以 http:// 或 https:// 开头"
            )

        if not (5 <= timeout <= 60):
            logger.warning(f"URL 获取请求失败：timeout 超出范围 ({timeout})")
            return create_url_fetcher_result(
                success=False,
                url=url,
                error="timeout 必须在 5-60 之间"
            )

        url_cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', url)
        if url_cleaned != url:
            logger.warning(f"URL 包含控制字符，已清理")
            url = url_cleaned

        browser_service = await get_global_browser_service()

        web_client = WebClient(config, browser_service=browser_service)
        article = await web_client.fetch(url, timeout)

        parser = HTMLParser()
        result = parser.parse(article, url, return_format, retain_images)

        logger.info(f"RESPONSE - SUCCESS - url={url}, title={result['title']}")
        return create_url_fetcher_result(
            True,
            result["url"],
            result["title"],
            result["summary"],
            result["content"],
            result["metadata"]
        )

    except URLValidationError as e:
        error_msg = f"{e!s}"
        logger.info(f"RESPONSE - FAILED - url={url}, error={error_msg}")
        return create_url_fetcher_result(False, url, error=error_msg)
    except FetchError as e:
        error_msg = f"{e!s}"
        logger.info(f"RESPONSE - FAILED - url={url}, error={error_msg}")
        return create_url_fetcher_result(False, url, error=error_msg)
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e!s}"
        logger.info(f"RESPONSE - FAILED - url={url}, error={error_msg}")
        return create_url_fetcher_result(False, url, error=error_msg)
