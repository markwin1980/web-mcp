"""Web-Search 模块 - 网页搜索功能。"""

from web_search.client import BingSearchClient
from web_search.config import BingSearchConfig
from web_search.web_search import web_search

__all__ = ["web_search", "BingSearchClient", "BingSearchConfig"]
