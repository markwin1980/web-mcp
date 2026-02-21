"""Bing 搜索的配置管理。"""

from dataclasses import dataclass


@dataclass
class BingSearchConfig:
    """Bing 搜索配置。"""

    # 搜索配置
    base_url: str = "https://cn.bing.com"
    """Bing 首页 URL"""

    # 超时配置
    timeout: int = 30000
    """页面加载超时时间（毫秒）"""

    # 延迟配置
    page_load_delay: float = 1.0
    """页面加载后等待时间（秒）"""

    result_parse_delay: float = 0.5
    """结果解析后等待时间（秒）"""

    results_per_page: int = 10
    """每页结果数量（Bing 默认为 10）"""

    max_results: int = 50
    """允许的最大搜索结果数量"""

    @classmethod
    def from_env(cls) -> "BingSearchConfig":
        """从环境变量创建配置。

        Returns:
            默认的 Bing 搜索配置
        """
        return cls()
