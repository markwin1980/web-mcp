"""Console 日志处理器 - 捕获和管理页面的 console 日志和异常。"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ConsoleLog:
    """单条 Console 日志记录。"""

    timestamp: datetime
    type: str  # "log", "info", "warn", "error", "debug", "pageerror"
    message: str
    stack: str | None = None
    location: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "type": self.type,
            "message": self.message,
            "stack": self.stack,
            "location": self.location,
        }


class ConsoleHandler:
    """Console 日志处理器。"""

    def __init__(self):
        self._logs: list[ConsoleLog] = []
        self._lock = asyncio.Lock()

    async def add_log(
        self,
        log_type: str,
        message: str,
        stack: str | None = None,
        location: str | None = None,
    ) -> None:
        """添加一条日志。

        Args:
            log_type: 日志类型 (log, info, warn, error, debug, pageerror)
            message: 日志消息
            stack: 堆栈信息（可选）
            location: 位置信息（可选）
        """
        log = ConsoleLog(
            timestamp=datetime.now(),
            type=log_type,
            message=message,
            stack=stack,
            location=location,
        )
        async with self._lock:
            self._logs.append(log)

    async def get_logs(
        self,
        log_type: str | None = None,
        limit: int | None = None,
    ) -> list[ConsoleLog]:
        """获取日志。

        Args:
            log_type: 按类型过滤（可选）
            limit: 返回数量限制（可选）

        Returns:
            日志列表
        """
        async with self._lock:
            logs = list(self._logs)

        if log_type:
            logs = [log for log in logs if log.type == log_type]

        if limit is not None:
            logs = logs[-limit:]

        return logs

    async def clear_logs(self) -> None:
        """清空所有日志。"""
        async with self._lock:
            self._logs.clear()

    def get_log_count(self) -> int:
        """获取日志总数。"""
        return len(self._logs)
