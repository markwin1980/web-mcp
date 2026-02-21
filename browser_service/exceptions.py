"""浏览器服务的自定义异常类。"""


class BrowserError(Exception):
    """浏览器错误的基类异常。"""
    pass


class PageCreationError(BrowserError):
    """页面创建错误。"""
    pass


class PageClosedError(BrowserError):
    """页面已关闭错误。"""
    pass


class BrowserInitializationError(BrowserError):
    """浏览器初始化错误。"""
    pass
