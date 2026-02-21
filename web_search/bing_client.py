"""Bing 搜索客户端 - 使用 Playwright 实现。"""

import asyncio
from typing import Any

from playwright.async_api import Page

from .config import BingSearchConfig
from .exceptions import BingSearchError, PageLoadError, ResultParseError


class BingClient:
    """使用 Playwright 实现的 Bing 搜索客户端。"""

    def __init__(
            self,
            search_config: BingSearchConfig | None = None,
            browser_service: Any = None,
    ):
        if browser_service is None:
            raise ValueError("browser_service 参数不能为 None")

        self.search_config = search_config or BingSearchConfig.from_env()
        self._browser_service = browser_service

    async def _perform_search_on_page(self, page: Page, query: str) -> None:
        try:
            await page.goto(
                self.search_config.base_url,
                timeout=self.search_config.timeout,
                wait_until="domcontentloaded"
            )

            await page.wait_for_selector("input[name='q'], #sb_form_q", timeout=5000)
            await page.fill("input[name='q'], #sb_form_q", query)
            await page.press("input[name='q'], #sb_form_q", "Enter")

            try:
                await page.wait_for_selector(
                    "li.b_algo",
                    timeout=self.search_config.page_load_delay * 1000
                )
            except Exception:
                pass

        except Exception as e:
            raise PageLoadError(f"首页搜索执行失败: {e}") from e

    async def _click_next_page(self, page: Page) -> bool:
        next_button = await page.query_selector(
            "a[class*='sb_pagN'], a[class*='pagN'], .sb_pagN, a[title='下一页']"
        )

        if not next_button:
            return False

        await next_button.click()

        try:
            await page.wait_for_selector(
                "li.b_algo",
                timeout=self.search_config.page_load_delay * 1000
            )
        except Exception:
            pass

        return True

    async def _get_result_list(self, page: Page) -> list[dict[str, Any]]:
        try:
            results: list[dict[str, Any]] = []

            try:
                await page.wait_for_selector("li.b_algo", timeout=5000)
                await asyncio.sleep(0.5)
            except Exception:
                return []

            result_elements = await page.query_selector_all("li.b_algo")

            for element in result_elements:
                try:
                    title_elem = await element.query_selector("h2 a")
                    if not title_elem:
                        continue

                    title = await title_elem.inner_text()
                    url = await title_elem.get_attribute("href")

                    if not title or not url:
                        continue

                    if not url.startswith(("http://", "https://")):
                        continue

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
                    continue

            return results

        except Exception as e:
            raise ResultParseError(f"解析搜索结果失败: {e}") from e

    async def search(
            self,
            query: str,
            num_results: int = 10,
    ) -> list[dict[str, Any]]:
        """执行搜索。

        Args:
            query: 搜索关键词
            num_results: 需要返回的结果数量

        Returns:
            搜索结果列表，每个结果包含 title, url, snippet, rank
        """
        all_results: list[dict[str, Any]] = []
        page = None

        try:
            # 创建页面（只创建一次，用于翻页）
            page = await self._browser_service.create_page()

            # 执行首次搜索
            await self._perform_search_on_page(page, query)
            page_results = await self._get_result_list(page)
            if not page_results:
                return []
            all_results.extend(page_results)

            # 翻页获取更多结果
            while len(all_results) < num_results:
                await asyncio.sleep(self.search_config.result_parse_delay)

                success = await self._click_next_page(page)
                if not success:
                    break

                page_results = await self._get_result_list(page)
                if not page_results:
                    break

                all_results.extend(page_results)

        except BingSearchError:
            raise
        except Exception as e:
            raise BingSearchError(f"搜索失败: {e}") from e
        finally:
            if page:
                await self._browser_service.release_page(page)

        for idx, result in enumerate(all_results):
            result["rank"] = idx + 1

        return all_results[:num_results]
