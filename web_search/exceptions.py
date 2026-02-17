"""web-search 的自定义异常类。"""


class BaiduSearchError(Exception):
    """百度搜索 API 错误的基类异常。"""

    pass


class BaiduSearchAuthError(BaiduSearchError):
    """百度搜索认证错误（API Key 无效）。"""

    pass


class BaiduSearchAPIError(BaiduSearchError):
    """百度搜索 API 返回错误。"""

    pass
