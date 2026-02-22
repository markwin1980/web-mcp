"""会话管理器 - 管理多个调试会话。"""

import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from browser_service import BrowserService, get_global_browser_service
from web_dev.dev_session import DevSession
from web_dev.exceptions import SessionCreationError, SessionNotFoundError


@dataclass
class SessionInfo:
    """会话信息。"""

    session_id: str
    created_at: datetime
    url: str | None = None
    title: str | None = None


class SessionManager:
    """会话管理器（全局单例）。"""

    _instance: ClassVar["SessionManager"] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __init__(self):
        if SessionManager._instance is not None:
            raise RuntimeError("Use SessionManager.get_instance() instead")

        self._sessions: dict[str, DevSession] = {}
        self._session_info: dict[str, SessionInfo] = {}
        self._operation_lock = asyncio.Lock()
        self._browser_service: BrowserService | None = None

    @classmethod
    def get_instance(cls) -> "SessionManager":
        """获取单例实例。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def create_session(self) -> str:
        """创建新的调试会话。

        Returns:
            会话 ID
        """
        async with self._operation_lock:
            if self._browser_service is None:
                self._browser_service = await get_global_browser_service()

            try:
                # 从浏览器服务获取页面
                page = await self._browser_service.create_page()

                # 生成会话 ID
                session_id = str(uuid.uuid4())

                # 创建调试会话
                dev_session = DevSession(session_id, page)

                # 存储会话
                self._sessions[session_id] = dev_session
                self._session_info[session_id] = SessionInfo(
                    session_id=session_id,
                    created_at=datetime.now(),
                )

                return session_id

            except Exception as e:
                raise SessionCreationError(f"Failed to create session: {e}") from e

    def get_session(self, session_id: str) -> DevSession:
        """获取指定的会话。

        Args:
            session_id: 会话 ID

        Returns:
            调试会话对象

        Raises:
            SessionNotFoundError: 会话不存在
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        return session

    def has_session(self, session_id: str) -> bool:
        """检查会话是否存在。

        Args:
            session_id: 会话 ID

        Returns:
            会话是否存在
        """
        return session_id in self._sessions

    async def close_session(self, session_id: str) -> None:
        """关闭会话。

        Args:
            session_id: 会话 ID

        Raises:
            SessionNotFoundError: 会话不存在
        """
        async with self._operation_lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise SessionNotFoundError(f"Session not found: {session_id}")

            try:
                # 清理会话资源
                await session.cleanup()

                # 释放页面回浏览器池
                if self._browser_service:
                    await self._browser_service.release_page(session.page)

            except Exception:
                # 即使释放页面失败，也要继续清理
                pass

            finally:
                # 从存储中移除
                del self._sessions[session_id]
                del self._session_info[session_id]

    def list_sessions(self) -> list[SessionInfo]:
        """列出所有活跃会话。

        Returns:
            会话信息列表
        """
        # 更新会话信息
        for session_id, session in self._sessions.items():
            info = self._session_info[session_id]
            try:
                info.url = session.page.url
                info.title = session.page.title if hasattr(session.page, "title") else None
            except Exception:
                pass

        return list(self._session_info.values())

    async def close_all_sessions(self) -> None:
        """关闭所有会话。"""
        session_ids = list(self._sessions.keys())
        for session_id in session_ids:
            try:
                await self.close_session(session_id)
            except Exception:
                pass

    def get_session_count(self) -> int:
        """获取活跃会话数量。"""
        return len(self._sessions)


# 全局单例访问函数


def get_session_manager() -> SessionManager:
    """获取会话管理器单例。"""
    return SessionManager.get_instance()


async def create_dev_session() -> str:
    """创建调试会话的便捷函数。"""
    manager = get_session_manager()
    return await manager.create_session()


async def close_dev_session(session_id: str) -> None:
    """关闭调试会话的便捷函数。"""
    manager = get_session_manager()
    await manager.close_session(session_id)
