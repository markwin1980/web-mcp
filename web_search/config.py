"""Bing 搜索的配置管理。"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class BingSearchConfig:
    """Bing 搜索配置。"""

    # Playwright 配置（固定值）
    browser_type: Literal["chromium"] = "chromium"
    """浏览器类型，固定使用 chromium"""

    headless: bool = True
    """是否使用无头模式"""

    timeout: int = 30000
    """页面加载超时时间（毫秒）"""

    # 搜索配置
    base_url: str = "https://cn.bing.com"
    """Bing 基础 URL"""

    search_url_template: str = "https://cn.bing.com/search?q={query}&first={offset}"
    """搜索 URL 模板，使用 first 参数控制偏移"""

    # User-Agent（固定配置）
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    """浏览器 User-Agent"""

    # 延迟配置
    page_load_delay: float = 1.0
    """页面加载后等待时间（秒）"""

    result_parse_delay: float = 0.5
    """结果解析后等待时间（秒）"""

    results_per_page: int = 10
    """每页结果数量（Bing 默认为 10）"""

    @classmethod
    def from_env(cls) -> "BingSearchConfig":
        """从环境变量创建配置。

        Returns:
            默认的 Bing 搜索配置
        """
        return cls()
