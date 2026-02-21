"""浏览器服务配置。"""

import os
from dataclasses import dataclass


@dataclass
class BrowserConfig:
    """浏览器服务配置。"""

    headless: bool = True
    max_cached_pages: int = 10
    initial_page_count: int = 1

    @classmethod
    def from_env(cls) -> "BrowserConfig":
        """从环境变量创建配置。

        支持的环境变量：
            BROWSER_HEADLESS: 是否使用无头模式，默认为 True。
                设置为 "1"、"true"、"yes"、"on" 时为 True，其他值为 False
        """
        headless_str = os.getenv("BROWSER_HEADLESS", "true").lower()
        headless = headless_str in ("1", "true", "yes", "on")

        return cls(headless=headless)
