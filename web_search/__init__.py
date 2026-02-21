"""Web-Search 模块 - 网页搜索功能。"""

from web_search.bing_client import BingClient
from web_search.config import BingSearchConfig
from web_search.web_search import web_search

__all__ = ["web_search", "BingClient", "BingSearchConfig"]
