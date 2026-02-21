"""浏览器服务 - 使用 Playwright 管理浏览器和页面池。"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

from playwright.async_api import Browser, Page
from playwright_stealth import Stealth

from .config import BrowserConfig
from .exception import BrowserError, BrowserInitializationError, PageCreationError

logger = logging.getLogger(__name__)


@dataclass
class PooledPage:
    """池化的页面对象。"""
    page: Page
    context: Any
    in_use: bool = False
    last_used: float = 0.0


class PagePool:
    """页面池管理器，复用页面以提高性能。"""

    def __init__(self, browser: Browser, stealth: Stealth, config: BrowserConfig):
        self._browser = browser
        self._stealth = stealth
        self._config = config
        self._pool: list[PooledPage] = []
        self._lock = asyncio.Lock()

    async def initialize(self):
        """初始化页面池，预先创建指定数量的页面。"""
        for _ in range(self._config.initial_page_count):
            context = await self._browser.new_context(
                user_agent=self._config.user_agent,
            )
            page = await context.new_page()
            await self._stealth.apply_stealth_async(page)

            pooled = PooledPage(
                page=page,
                context=context,
                in_use=False,
                last_used=0.0
            )
            self._pool.append(pooled)

    async def acquire(self) -> Page:
        """获取一个页面（优先复用池中的空闲页面）。"""
        async with self._lock:
            for pooled in self._pool:
                if not pooled.in_use:
                    pooled.in_use = True
                    pooled.last_used = time.time()
                    return pooled.page

            try:
                context = await self._browser.new_context(
                    user_agent=self._config.user_agent,
                )
                page = await context.new_page()
                await self._stealth.apply_stealth_async(page)

                pooled = PooledPage(
                    page=page,
                    context=context,
                    in_use=True,
                    last_used=time.time()
                )
                self._pool.append(pooled)
                return page
            except Exception as e:
                raise PageCreationError(f"创建新页面失败: {e}") from e

    async def release(self, page: Page):
        """释放页面回池中。"""
        async with self._lock:
            for pooled in self._pool:
                if pooled.page == page:
                    pooled.in_use = False
                    pooled.last_used = time.time()
                    break

            await self._cleanup_if_needed()

    async def _cleanup_if_needed(self):
        """如果缓存的页面数超过配置，关闭最旧的未使用页面。"""
        if len(self._pool) <= self._config.max_cached_pages:
            return

        unused = [p for p in self._pool if not p.in_use]
        excess_count = len(self._pool) - self._config.max_cached_pages
        to_close = min(excess_count, len(unused))

        if to_close == 0:
            return

        unused.sort(key=lambda p: p.last_used)
        for pooled in unused[:to_close]:
            try:
                await pooled.page.close()
                await pooled.context.close()
            except Exception:
                pass
            self._pool.remove(pooled)

    async def close_all(self):
        """关闭池中的所有页面。"""
        async with self._lock:
            for pooled in self._pool:
                try:
                    await pooled.page.close()
                    await pooled.context.close()
                except Exception:
                    pass
            self._pool.clear()


class BrowserService:
    """浏览器服务，使用 Playwright 管理浏览器生命周期和页面池。"""

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or BrowserConfig.from_env()
        self._browser: Browser | None = None
        self._playwright = None
        self._stealth = Stealth()
        self._page_pool: PagePool | None = None

    @property
    def is_initialized(self) -> bool:
        """检查浏览器是否已初始化。"""
        return self._browser is not None

    async def initialize(self):
        """初始化浏览器实例。"""
        if self._browser is not None:
            return

        try:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()

            if self.config.browser_type == "chromium":
                self._browser = await self._playwright.chromium.launch(
                    headless=self.config.headless,
                )
            elif self.config.browser_type == "firefox":
                self._browser = await self._playwright.firefox.launch(
                    headless=self.config.headless,
                )
            elif self.config.browser_type == "webkit":
                self._browser = await self._playwright.webkit.launch(
                    headless=self.config.headless,
                )
            else:
                raise BrowserInitializationError(
                    f"不支持的浏览器类型: {self.config.browser_type}"
                )

            self._page_pool = PagePool(
                browser=self._browser,
                stealth=self._stealth,
                config=self.config
            )

            await self._page_pool.initialize()

            logger.info(
                f"浏览器已初始化 (type={self.config.browser_type}, "
                f"headless={self.config.headless})"
            )

        except Exception as e:
            raise BrowserInitializationError(f"浏览器初始化失败: {e}") from e

    async def create_page(self) -> Page:
        """从页面池获取一个页面。"""
        if self._page_pool is None:
            raise BrowserError(
                "浏览器未初始化，请先调用 initialize() 方法"
            )
        return await self._page_pool.acquire()

    async def release_page(self, page: Page):
        """释放页面回池中。"""
        if self._page_pool:
            await self._page_pool.release(page)

    async def close(self):
        """关闭浏览器和 Playwright 实例。"""
        if self._page_pool:
            await self._page_pool.close_all()
            self._page_pool = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        logger.info("浏览器已关闭")

    async def __aenter__(self) -> "BrowserService":
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
