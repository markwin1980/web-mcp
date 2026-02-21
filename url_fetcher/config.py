"""url-fetcher 的配置管理。"""

from dataclasses import dataclass


@dataclass
class FetcherConfig:
    """url-fetcher 的配置设置。"""

    default_timeout: int = 20
