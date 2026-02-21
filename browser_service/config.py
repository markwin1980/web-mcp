"""浏览器服务配置。"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class BrowserConfig:
    """浏览器服务配置。"""

    browser_type: Literal["chromium", "firefox", "webkit"] = "chromium"
    headless: bool = True

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    max_cached_pages: int = 10
    initial_page_count: int = 1

    @classmethod
    def from_env(cls) -> "BrowserConfig":
        """从环境变量创建配置。"""
        return cls()
