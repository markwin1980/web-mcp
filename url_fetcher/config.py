"""url-fetcher 的配置管理。"""

from dataclasses import dataclass


@dataclass
class Config:
    """url-fetcher 的配置设置。"""

    user_agent: str = "URL-Fetcher/1.0"
    proxy_url: str | None = None
    max_content_length: int = 1_000_000
    cache_ttl: int = 3600
    default_timeout: int = 20
