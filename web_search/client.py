"""Bing 搜索客户端 - 使用 Playwright 实现。"""

import asyncio
import urllib.parse
from typing import Any

from playwright.async_api import async_playwright, Browser, Page
from playwright_stealth import Stealth

from .config import BingSearchConfig
from .exceptions import BingSearchError, PageLoadError, ResultParseError


class BingSearchClient:
    """使用 Playwright 实现的 Bing 搜索客户端。"""

    def __init__(self, config: BingSearchConfig | None = None):
        """初始化 Bing 搜索客户端。

        Args:
            config: Bing 搜索配置，如果为 None 则使用默认配置
        """
        self.config = config or BingSearchConfig.from_env()
        self._browser: Browser | None = None
        self._stealth = Stealth()

    async def _create_page(self) -> Page:
        """创建配置好的页面对象（应用 stealth 和 User-Agent）。

        Returns:
            配置好的 Playwright Page 对象
        """
        if self._browser is None:
            raise RuntimeError("浏览器未初始化，请使用 async with 语句创建客户端")

        context = await self._browser.new_context(
            user_agent=self.config.user_agent,
        )
        page = await context.new_page()
        await self._stealth.apply_stealth_async(page)  # 应用 stealth 绕过反爬检测
        return page

    def _build_search_url(self, query: str, offset: int) -> str:
        """构造搜索 URL。

        Args:
            query: 搜索关键词
            offset: 结果偏移量（0, 10, 20...）

        Returns:
            完整的搜索 URL
        """
        encoded_query = urllib.parse.quote(query)
        return self.config.search_url_template.format(
            query=encoded_query,
            offset=offset
        )

    async def _get_result_list(
            self,
            page: Page,
    ) -> list[dict[str, Any]]:
        """从页面提取搜索结果列表。

        Args:
            page: Playwright 页面对象

        Returns:
            搜索结果列表，每个结果包含 title, url, snippet

        Raises:
            ResultParseError: 结果解析失败
        """
        try:
            results: list[dict[str, Any]] = []

            # 等待搜索结果加载（超时返回空列表）
            try:
                await page.wait_for_selector("li.b_algo", timeout=5000)
            except Exception:
                # 没有找到结果元素，返回空列表
                return []

            # 获取所有搜索结果
            result_elements = await page.query_selector_all("li.b_algo")

            for element in result_elements:
                try:
                    # 提取标题和链接
                    title_elem = await element.query_selector("h2 a")
                    if not title_elem:
                        continue

                    title = await title_elem.inner_text()
                    url = await title_elem.get_attribute("href")

                    if not title or not url:
                        continue

                    # 提取摘要
                    snippet_elem = await element.query_selector("p.b_algoSlug, div.b_caption p")
                    snippet = ""
                    if snippet_elem:
                        snippet = await snippet_elem.inner_text()

                    results.append({
                        "title": title.strip(),
                        "url": url.strip(),
                        "snippet": snippet.strip(),
                    })

                except Exception:
                    # 跳过单个结果的解析错误
                    continue

            return results

        except Exception as e:
            raise ResultParseError(f"解析搜索结果失败: {e}") from e

    async def search(
            self,
            query: str,
            num_results: int = 10,
    ) -> list[dict[str, Any]]:
        """执行搜索，支持翻页获取结果。

        Args:
            query: 搜索关键词
            num_results: 需要返回的结果数量

        Returns:
            搜索结果列表，每个结果包含 title, url, snippet, rank

        Raises:
            BingSearchError: 搜索失败
        """
        all_results: list[dict[str, Any]] = []
        offset = 1

        try:
            async with async_playwright() as p:
                # 启动浏览器
                self._browser = await p.chromium.launch(
                    headless=self.config.headless,
                )

                try:
                    while len(all_results) < num_results:
                        # 创建页面
                        page = await self._create_page()

                        try:
                            # 构造搜索 URL
                            url = self._build_search_url(query, offset)

                            # 导航到搜索页面
                            try:
                                await page.goto(
                                    url,
                                    timeout=self.config.timeout,
                                    wait_until="domcontentloaded"
                                )
                                await asyncio.sleep(self.config.page_load_delay)
                            except Exception as e:
                                raise PageLoadError(f"页面加载失败: {e}") from e

                            # 提取当前页结果
                            page_results = await self._get_result_list(page)

                            if not page_results:
                                # 没有更多结果
                                break

                            all_results.extend(page_results)
                            offset += self.config.results_per_page

                            # 等待一下再翻页
                            await asyncio.sleep(self.config.result_parse_delay)

                        finally:
                            await page.close()

                finally:
                    await self._browser.close()
                    self._browser = None

        except BingSearchError:
            raise
        except Exception as e:
            raise BingSearchError(f"搜索失败: {e}") from e

        # 添加 rank 字段
        for idx, result in enumerate(all_results):
            result["rank"] = idx + 1

        # 返回请求数量的结果
        return all_results[:num_results]

    async def close(self):
        """关闭浏览器。"""
        if self._browser:
            await self._browser.close()
            self._browser = None

    async def __aenter__(self) -> "BingSearchClient":
        """异步上下文管理器入口。"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口。"""
        await self.close()
