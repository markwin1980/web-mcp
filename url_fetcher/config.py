"""url-fetcher 的配置管理。"""

from dataclasses import dataclass


@dataclass
class Config:
    """url-fetcher 的配置设置。"""

    default_timeout: int = 20
