"""浏览器服务配置。"""

import os
from dataclasses import dataclass


@dataclass
class BrowserConfig:
    """浏览器服务配置。"""

    headless: bool = False
    max_cached_pages: int = 10
    initial_page_count: int = 1
    viewport_width: int = 1280
    viewport_height: int = 720

    @classmethod
    def from_env(cls) -> "BrowserConfig":
        """从环境变量创建配置。

        支持的环境变量：
            BROWSER_HEADLESS: 是否使用无头模式，默认为 False。
                设置为 "1"、"true"、"yes"、"on" 时为 True，其他值为 False
            BROWSER_MAX_CACHED_PAGES: 最大缓存页面数，默认为 10，最大不超过 100
            BROWSER_INITIAL_PAGE_COUNT: 初始页面数量，默认为 1，最大不超过 10
            BROWSER_VIEWPORT_WIDTH: 浏览器视口宽度，默认为 1280
            BROWSER_VIEWPORT_HEIGHT: 浏览器视口高度，默认为 720
        """
        headless_str = os.getenv("BROWSER_HEADLESS", "false").lower()
        headless = headless_str in ("1", "true", "yes", "on")

        # 最大缓存页面数，默认 10，最大不超过 100
        max_cached_pages = int(os.getenv("BROWSER_MAX_CACHED_PAGES", "10"))
        max_cached_pages = min(max_cached_pages, 100)

        # 初始页面数量，默认 1，最大不超过 10
        initial_page_count = int(os.getenv("BROWSER_INITIAL_PAGE_COUNT", "1"))
        initial_page_count = min(initial_page_count, 10)

        # 浏览器视口宽度，默认 1280
        viewport_width = int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1280"))

        # 浏览器视口高度，默认 720
        viewport_height = int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "720"))

        return cls(
            headless=headless,
            max_cached_pages=max_cached_pages,
            initial_page_count=initial_page_count,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
        )
