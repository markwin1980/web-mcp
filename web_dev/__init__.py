"""Web-Dev 模块 - 提供网页开发调试工具。"""

from .config import WebDevConfig
from .exceptions import (
    WebDevError,
    SessionNotFoundError,
    SessionCreationError,
    InvalidActionError,
    ElementNotFoundError,
    NavigationError,
    ScreenshotError,
    ActionExecutionError,
)
from .session_manager import (
    SessionManager,
    get_session_manager,
    create_dev_session,
    close_dev_session,
)
from .dev_session import DevSession
from .console_handler import ConsoleHandler, ConsoleLog
from .web_dev import web_dev

__all__ = [
    "WebDevConfig",
    "WebDevError",
    "SessionNotFoundError",
    "SessionCreationError",
    "InvalidActionError",
    "ElementNotFoundError",
    "NavigationError",
    "ScreenshotError",
    "ActionExecutionError",
    "SessionManager",
    "get_session_manager",
    "create_dev_session",
    "close_dev_session",
    "DevSession",
    "ConsoleHandler",
    "ConsoleLog",
    "web_dev",
]
