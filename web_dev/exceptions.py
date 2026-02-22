"""Web-Dev 模块的自定义异常类。"""


class WebDevError(Exception):
    """Web-Dev 错误的基类异常。"""
    pass


class SessionNotFoundError(WebDevError):
    """会话不存在错误。"""
    pass


class SessionCreationError(WebDevError):
    """会话创建错误。"""
    pass


class InvalidActionError(WebDevError):
    """无效的操作类型错误。"""
    pass


class ElementNotFoundError(WebDevError):
    """元素未找到错误。"""
    pass


class NavigationError(WebDevError):
    """导航错误。"""
    pass


class ScreenshotError(WebDevError):
    """截图错误。"""
    pass


class ActionExecutionError(WebDevError):
    """操作执行错误。"""
    pass
