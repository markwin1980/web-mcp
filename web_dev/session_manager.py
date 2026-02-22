import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Optional

from browser_service import BrowserService, get_global_browser_service
from web_dev.dev_session import DevSession
from web_dev.exceptions import SessionCreationError, SessionNotFoundError


@dataclass
class SessionInfo:
    session_id: str
    created_at: datetime
    url: str | None = None
    title: str | None = None


class SessionManager:
    _instance: ClassVar[Optional["SessionManager"]] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __init__(self, browser_service: BrowserService):
        if SessionManager._instance is not None:
            raise RuntimeError("Use SessionManager.get_instance() instead")

        self._sessions: dict[str, DevSession] = {}
        self._session_info: dict[str, SessionInfo] = {}
        self._operation_lock = asyncio.Lock()
        self._browser_service = browser_service

    @classmethod
    async def get_instance(cls) -> "SessionManager":
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    browser_service = await get_global_browser_service()
                    cls._instance = cls(browser_service)
        assert cls._instance is not None
        return cls._instance

    async def create_session(self) -> str:
        async with self._operation_lock:
            try:
                page = await self._browser_service.create_page()
                session_id = str(uuid.uuid4())
                dev_session = DevSession(session_id, page)
                self._sessions[session_id] = dev_session
                self._session_info[session_id] = SessionInfo(
                    session_id=session_id,
                    created_at=datetime.now(),
                )
                return session_id
            except Exception as e:
                raise SessionCreationError(f"Failed to create session: {e}") from e

    def get_session(self, session_id: str) -> DevSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        return session

    def has_session(self, session_id: str) -> bool:
        return session_id in self._sessions

    async def close_session(self, session_id: str) -> None:
        async with self._operation_lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise SessionNotFoundError(f"Session not found: {session_id}")

            try:
                await session.cleanup()
                await self._browser_service.release_page(session.page)
            except Exception:
                pass
            finally:
                del self._sessions[session_id]
                del self._session_info[session_id]

    def update_session_info(self, session_id: str, url: str | None = None, title: str | None = None) -> None:
        """更新会话信息。"""
        if session_id in self._session_info:
            if url is not None:
                self._session_info[session_id].url = url
            if title is not None:
                self._session_info[session_id].title = title

    async def close_all_sessions(self) -> None:
        session_ids = list(self._sessions.keys())
        for session_id in session_ids:
            try:
                await self.close_session(session_id)
            except Exception:
                pass

    def get_session_count(self) -> int:
        return len(self._sessions)


async def get_session_manager() -> SessionManager:
    return await SessionManager.get_instance()


async def create_dev_session() -> str:
    manager = await get_session_manager()
    return await manager.create_session()


async def close_dev_session(session_id: str) -> None:
    manager = await get_session_manager()
    await manager.close_session(session_id)
