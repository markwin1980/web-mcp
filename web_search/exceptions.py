"""Bing 搜索的自定义异常类。"""


class BingSearchError(Exception):
    """Bing 搜索错误的基类异常。"""

    pass


class PageLoadError(BingSearchError):
    """页面加载错误。"""

    pass


class ResultParseError(BingSearchError):
    """结果解析错误。"""

    pass
