"""使用 Playwright + Readability.js 获取网页内容。"""

import os
from pathlib import Path
from typing import Optional

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from browser_service import BrowserService
from url_fetcher.config import Config
from url_fetcher.exceptions import FetchError, URLValidationError

READABILITY_JS_PATH = Path(os.getcwd()) / "res" / "Readability.js"


class WebClient:
    """使用 Playwright + Readability.js 获取网页。"""

    def __init__(self, config: Optional[Config] = None, *, browser_service: BrowserService):
        self.config = config or Config()
        self._browser_service = browser_service

        if not READABILITY_JS_PATH.exists():
            raise FetchError(f"Readability.js 不存在: {READABILITY_JS_PATH}")
        with open(READABILITY_JS_PATH, "r", encoding="utf-8") as f:
            self._readability_js = f.read()

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
        if not url.startswith(("http://", "https://")):
            raise URLValidationError(f"无效的 URL 协议：{url}")

        page = None
        try:
            page = await self._browser_service.create_page()

            # 导航到页面
            await page.goto(
                url,
                timeout=timeout * 1000,
                wait_until="domcontentloaded"
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
