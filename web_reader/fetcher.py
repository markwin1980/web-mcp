"""支持缓存的网页获取模块。"""

from datetime import datetime, timedelta
from typing import Optional

import aiohttp

from web_reader.config import Config
from web_reader.exceptions import FetchError, URLValidationError


class WebFetcher:
    """使用 HTTP 请求和缓存获取网页。"""

    def __init__(self, config: Optional[Config] = None):
        """初始化网页获取器。

        Args:
            config: 可选的配置。如果不提供，使用默认配置。
        """
        self.config = config or Config()
        self._cache: dict[str, tuple[str, datetime]] = {}

    async def fetch(self, url: str, timeout: int, no_cache: bool = False) -> str:
        """获取网页的 HTML 内容。

        Args:
            url: 要获取的 URL
            timeout: 请求超时时间（秒）
            no_cache: 如果为 True，绕过缓存

        Returns:
            HTML 内容字符串

        Raises:
            URLValidationError: 如果 URL 无效
            FetchError: 如果获取失败
        """
        self._validate_url(url)

        # 检查缓存
        if not no_cache:
            cached = self._get_from_cache(url)
            if cached is not None:
                return cached

        # 获取网页
        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.get(
                    url,
                    headers={"User-Agent": self.config.user_agent},
                ) as response:
                    response.raise_for_status()

                    html = await response.text()

                    # 检查内容长度
                    if len(html) > self.config.max_content_length:
                        raise FetchError(f"内容过大：{len(html)} 字节")

                    # 存储到缓存
                    self._store_in_cache(url, html)

                    return html

        except aiohttp.ClientTimeout:
            raise FetchError(f"获取 {url} 时超时")
        except aiohttp.ClientResponseError as e:
            raise FetchError(f"获取 {url} 时 HTTP 错误 {e.status}")
        except aiohttp.ClientError as e:
            raise FetchError(f"获取 {url} 时请求错误：{e!s}")
        except Exception as e:
            raise FetchError(f"获取 {url} 时发生意外错误：{e!s}")

    def _validate_url(self, url: str) -> None:
        """验证 URL。

        Args:
            url: 要验证的 URL

        Raises:
            URLValidationError: 如果 URL 无效
        """
        if not url.startswith(("http://", "https://")):
            raise URLValidationError(f"无效的 URL 协议：{url}")

    def _get_from_cache(self, url: str) -> Optional[str]:
        """从缓存获取内容（如果存在且未过期）。

        Args:
            url: 要检查缓存的 URL

        Returns:
            如果缓存有效则返回缓存的 HTML，否则返回 None
        """
        if url not in self._cache:
            return None

        html, timestamp = self._cache[url]
        if datetime.now() - timestamp >= timedelta(seconds=self.config.cache_ttl):
            # 缓存已过期
            del self._cache[url]
            return None

        return html

    def _store_in_cache(self, url: str, html: str) -> None:
        """将 HTML 内容存储到缓存。

        Args:
            url: 要缓存的 URL
            html: 要缓存的 HTML 内容
        """
        self._cache[url] = (html, datetime.now())

    def clear_cache(self) -> None:
        """清空缓存。"""
        self._cache.clear()
