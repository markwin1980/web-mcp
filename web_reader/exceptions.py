"""web-reader 的自定义异常类。"""


class WebReaderError(Exception):
    """web-reader 错误的基类异常。"""

    pass


class URLValidationError(WebReaderError):
    """URL 验证失败时抛出。"""

    pass


class FetchError(WebReaderError):
    """获取网页失败时抛出。"""

    pass


class ParseError(WebReaderError):
    """解析 HTML 内容失败时抛出。"""

    pass
