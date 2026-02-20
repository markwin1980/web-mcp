"""url-fetcher 的自定义异常类。"""


class URLFetcherError(Exception):
    """url-fetcher 错误的基类异常。"""

    pass


class URLValidationError(URLFetcherError):
    """URL 验证失败时抛出。"""

    pass


class FetchError(URLFetcherError):
    """获取网页失败时抛出。"""

    pass


class ParseError(URLFetcherError):
    """解析 HTML 内容失败时抛出。"""

    pass
