"""浏览器服务模块 - 提供浏览器和页面池管理功能。"""

import asyncio

from .browser_service import BrowserService
from .config import BrowserConfig
from .exceptions import (
    BrowserError,
    BrowserInitializationError,
    PageClosedError,
    PageCreationError,
)

_global_browser_service: BrowserService | None = None
_browser_service_lock = asyncio.Lock()


async def get_global_browser_service() -> BrowserService:
    """获取全局浏览器服务实例（单例模式，线程安全）。"""
    global _global_browser_service
    async with _browser_service_lock:
        if _global_browser_service is None:
            _global_browser_service = BrowserService()
        return _global_browser_service


async def initialize_global_browser():
    """初始化全局浏览器服务。"""
    service = await get_global_browser_service()
    if not service.is_initialized:
        await service.initialize()


async def close_global_browser():
    """关闭全局浏览器服务。"""
    global _global_browser_service
    async with _browser_service_lock:
        if _global_browser_service and _global_browser_service.is_initialized:
            await _global_browser_service.close()
        _global_browser_service = None


__all__ = [
    "BrowserService",
    "BrowserConfig",
    "BrowserError",
    "BrowserInitializationError",
    "PageClosedError",
    "PageCreationError",
    "get_global_browser_service",
    "initialize_global_browser",
    "close_global_browser",
]
