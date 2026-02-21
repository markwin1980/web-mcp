"""使用 Playwright + Readability.js 获取网页内容。"""

import ipaddress
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from browser_service import BrowserService
from url_fetcher.config import FetcherConfig
from url_fetcher.exceptions import FetchError, URLValidationError, UnsafeURLError

# 获取项目根目录（从当前文件路径向上两级）
READABILITY_JS_PATH = Path(__file__).parent.parent / "res" / "Readability.js"

# 模块级缓存，只加载一次 Readability.js
_readability_js_cache: Optional[str] = None


def _load_readability_js() -> str:
    """加载 Readability.js 脚本（使用模块级缓存）。

    Returns:
        Readability.js 脚本内容

    Raises:
        FetchError: 文件不存在时抛出
    """
    global _readability_js_cache

    if _readability_js_cache is None:
        if not READABILITY_JS_PATH.exists():
            raise FetchError(f"Readability.js 不存在: {READABILITY_JS_PATH}")
        with open(READABILITY_JS_PATH, "r", encoding="utf-8") as f:
            _readability_js_cache = f.read()

    return _readability_js_cache


def _is_safe_url(url: str) -> bool:
    """验证 URL 是否安全（防止 SSRF 攻击）。

    Args:
        url: 要验证的 URL

    Returns:
        URL 是否安全
    """
    try:
        parsed = urlparse(url)

        # 只允许 http 和 https 协议
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # 检查是否是内网 IP 地址
        try:
            ip = ipaddress.ip_address(hostname)
            # 拒绝私有地址、回环地址和链路本地地址
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            # 不是 IP 地址，是域名，允许通过
            pass

        return True

    except Exception:
        return False


class WebClient:
    """使用 Playwright + Readability.js 获取网页。"""

    def __init__(self, config: Optional[FetcherConfig] = None, *, browser_service: BrowserService):
        self.config = config or FetcherConfig()
        self._browser_service = browser_service
        # 延迟加载，只在使用时才加载 JS
        self._readability_js: Optional[str] = None

    async def fetch(self, url: str, timeout: int) -> dict:
        """获取网页的文章内容（使用 Readability.js）。

        Returns:
            Readability.js 返回的字典，包含:
            - title: 标题
            - content: HTML 格式的正文
            - textContent: 纯文本正文
            - excerpt: 摘要
            - byline: 作者
            - length: 长度
        """
        # 延迟加载 Readability.js（使用模块级缓存）
        if self._readability_js is None:
            self._readability_js = _load_readability_js()

        # 验证 URL 安全性
        if not _is_safe_url(url):
            if not url.startswith(("http://", "https://")):
                raise URLValidationError(f"无效的 URL 协议：{url}")
            raise UnsafeURLError(f"URL 指向不安全的地址（内网地址等）：{url}")

        page = None
        try:
            page = await self._browser_service.create_page()

            # 导航到页面,等待网络空闲(处理自动跳转)
            await page.goto(
                url,
                timeout=timeout * 1000,
                wait_until="networkidle"
            )

            # 注入 Readability.js
            await page.evaluate(self._readability_js)

            # 在页面中运行 Readability.js 提取文章
            article = await page.evaluate("""() => {
                const article = new Readability(document.cloneNode(true)).parse();
                return article;
            }""")

            if not article:
                raise FetchError("Readability.js 未能提取文章内容")

            return article

        except PlaywrightTimeoutError:
            raise FetchError(f"获取 {url} 时超时")
        except FetchError:
            raise
        except Exception as e:
            raise FetchError(f"获取 {url} 时发生错误：{e!s}")
        finally:
            if page:
                await self._browser_service.release_page(page)
