"""Web-Dev 工具函数 - 提供 MCP 工具接口。"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from web_dev.config import WebDevConfig
from web_dev.console_handler import ConsoleLog
from web_dev.dev_session import ElementInfo, PageInfo
from web_dev.exceptions import (
    WebDevError,
    SessionNotFoundError,
    InvalidActionError,
    ElementNotFoundError,
    NavigationError,
    ScreenshotError,
    ActionExecutionError,
)
from web_dev.session_manager import get_session_manager

config = WebDevConfig()

logger = logging.getLogger("web_dev")
logger.setLevel(logging.INFO)
if not logger.handlers:
    try:
        log_dir = Path("log")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"web_dev_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    except (OSError, PermissionError):
        logger.addHandler(logging.NullHandler())


def create_web_dev_result(
    success: bool,
    action: str,
    session_id: str | None = None,
    data: Any = None,
    error: str | None = None,
) -> str:
    """创建 Web-Dev 结果的 JSON 字符串。"""
    result = {
        "success": success,
        "action": action,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "error": error,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def _serialize_element_info(info: ElementInfo) -> dict[str, Any]:
    """序列化 ElementInfo 对象。"""
    return {
        "tag_name": info.tag_name,
        "id": info.id,
        "classes": info.classes,
        "text": info.text,
        "inner_html": info.inner_html,
        "attributes": info.attributes,
        "bounding_box": info.bounding_box,
        "css_style": info.css_style,
        "visible": info.visible,
        "enabled": info.enabled,
    }


def _serialize_page_info(info: PageInfo) -> dict[str, Any]:
    """序列化 PageInfo 对象。"""
    return {
        "url": info.url,
        "title": info.title,
        "viewport_size": info.viewport_size,
        "user_agent": info.user_agent,
        "cookies": info.cookies,
    }


def _serialize_console_logs(logs: list[ConsoleLog]) -> list[dict[str, Any]]:
    """序列化 ConsoleLog 列表。"""
    return [log.to_dict() for log in logs]


async def web_dev(
    action: str,
    session_id: str | None = None,
    **kwargs,
) -> str:
    """网页开发调试工具 - 单一综合入口。

    Args:
        action: 操作类型
        session_id: 会话ID（除 create_session 外都需要）
        **kwargs: 具体操作的参数

    Returns:
        JSON 格式的结果
    """
    logger.info(f"REQUEST - action={action}, session_id={session_id}")

    try:
        manager = get_session_manager()

        # ========== 会话管理 ==========

        if action == "create_session":
            new_session_id = await manager.create_session()
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={new_session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=new_session_id,
                data={"session_id": new_session_id},
            )

        # 以下操作都需要 session_id
        if not session_id:
            raise InvalidActionError("session_id is required for this action")

        if action == "close_session":
            await manager.close_session(session_id)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
            )

        if action == "list_sessions":
            sessions = manager.list_sessions()
            session_list = [
                {
                    "session_id": s.session_id,
                    "created_at": s.created_at.isoformat(),
                    "url": s.url,
                    "title": s.title,
                }
                for s in sessions
            ]
            logger.info(f"RESPONSE - SUCCESS - action={action}, count={len(session_list)}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"sessions": session_list, "count": len(session_list)},
            )

        # 获取会话
        session = manager.get_session(session_id)

        # ========== 导航操作 ==========

        if action == "navigate":
            url = kwargs.get("url")
            if not url:
                raise InvalidActionError("url is required for navigate action")
            timeout = kwargs.get("timeout", 30000)
            wait_until = kwargs.get("wait_until", "load")
            try:
                await session.navigate(url, timeout=timeout, wait_until=wait_until)
            except Exception as e:
                raise NavigationError(f"Navigation failed: {e}") from e
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, url={url}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"url": url},
            )

        if action == "go_back":
            await session.go_back()
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
            )

        if action == "go_forward":
            await session.go_forward()
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
            )

        if action == "reload":
            await session.reload()
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
            )

        # ========== 元素操作 ==========

        if action == "click":
            selector = kwargs.get("selector")
            if not selector:
                raise InvalidActionError("selector is required for click action")
            timeout = kwargs.get("timeout", 30000)
            force = kwargs.get("force", False)
            no_wait_after = kwargs.get("no_wait_after", False)
            await session.click(
                selector,
                timeout=timeout,
                force=force,
                no_wait_after=no_wait_after,
            )
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"selector": selector},
            )

        if action == "fill":
            selector = kwargs.get("selector")
            value = kwargs.get("value")
            if not selector:
                raise InvalidActionError("selector is required for fill action")
            if value is None:
                raise InvalidActionError("value is required for fill action")
            timeout = kwargs.get("timeout", 30000)
            await session.fill(selector, value, timeout=timeout)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"selector": selector},
            )

        if action == "type_text":
            selector = kwargs.get("selector")
            text = kwargs.get("text")
            if not selector:
                raise InvalidActionError("selector is required for type_text action")
            if text is None:
                raise InvalidActionError("text is required for type_text action")
            delay = kwargs.get("delay", 0)
            timeout = kwargs.get("timeout", 30000)
            await session.type_text(selector, text, delay=delay, timeout=timeout)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"selector": selector},
            )

        if action == "clear":
            selector = kwargs.get("selector")
            if not selector:
                raise InvalidActionError("selector is required for clear action")
            timeout = kwargs.get("timeout", 30000)
            await session.clear(selector, timeout=timeout)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"selector": selector},
            )

        if action == "select_option":
            selector = kwargs.get("selector")
            if not selector:
                raise InvalidActionError("selector is required for select_option action")
            values = kwargs.get("values")
            labels = kwargs.get("labels")
            if values is None and labels is None:
                raise InvalidActionError("values or labels is required for select_option action")
            timeout = kwargs.get("timeout", 30000)
            await session.select_option(
                selector,
                values=values,
                labels=labels,
                timeout=timeout,
            )
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"selector": selector},
            )

        if action == "check":
            selector = kwargs.get("selector")
            if not selector:
                raise InvalidActionError("selector is required for check action")
            timeout = kwargs.get("timeout", 30000)
            await session.check(selector, timeout=timeout)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"selector": selector},
            )

        if action == "uncheck":
            selector = kwargs.get("selector")
            if not selector:
                raise InvalidActionError("selector is required for uncheck action")
            timeout = kwargs.get("timeout", 30000)
            await session.uncheck(selector, timeout=timeout)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"selector": selector},
            )

        if action == "hover":
            selector = kwargs.get("selector")
            if not selector:
                raise InvalidActionError("selector is required for hover action")
            timeout = kwargs.get("timeout", 30000)
            await session.hover(selector, timeout=timeout)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"selector": selector},
            )

        if action == "drag_and_drop":
            source_selector = kwargs.get("source_selector")
            target_selector = kwargs.get("target_selector")
            if not source_selector:
                raise InvalidActionError("source_selector is required for drag_and_drop action")
            if not target_selector:
                raise InvalidActionError("target_selector is required for drag_and_drop action")
            timeout = kwargs.get("timeout", 30000)
            await session.drag_and_drop(
                source_selector,
                target_selector,
                timeout=timeout,
            )
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={
                    "source_selector": source_selector,
                    "target_selector": target_selector,
                },
            )

        if action == "focus":
            selector = kwargs.get("selector")
            if not selector:
                raise InvalidActionError("selector is required for focus action")
            timeout = kwargs.get("timeout", 30000)
            await session.focus(selector, timeout=timeout)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"selector": selector},
            )

        # ========== 键盘和鼠标操作 ==========

        if action == "press_key":
            key = kwargs.get("key")
            if not key:
                raise InvalidActionError("key is required for press_key action")
            delay = kwargs.get("delay", 0)
            await session.press_key(key, delay=delay)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, key={key}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"key": key},
            )

        if action == "scroll":
            x = kwargs.get("x")
            y = kwargs.get("y")
            if x is None and y is None:
                raise InvalidActionError("x or y is required for scroll action")
            await session.scroll(x=x, y=y)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"x": x, "y": y},
            )

        # ========== 查询操作 ==========

        if action == "get_element_info":
            selector = kwargs.get("selector")
            if not selector:
                raise InvalidActionError("selector is required for get_element_info action")
            timeout = kwargs.get("timeout", 30000)
            info = await session.get_element_info(selector, timeout=timeout)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"element": _serialize_element_info(info)},
            )

        if action == "get_page_info":
            info = await session.get_page_info()
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"page": _serialize_page_info(info)},
            )

        if action == "search_elements":
            selector = kwargs.get("selector")
            if not selector:
                raise InvalidActionError("selector is required for search_elements action")
            timeout = kwargs.get("timeout", 5000)
            elements = await session.search_elements(selector, timeout=timeout)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, count={len(elements)}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"elements": elements, "count": len(elements)},
            )

        # ========== Console 日志 ==========

        if action == "get_console_logs":
            log_type = kwargs.get("type")
            limit = kwargs.get("limit")
            logs = await session.console_handler.get_logs(
                log_type=log_type,
                limit=limit,
            )
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, count={len(logs)}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"logs": _serialize_console_logs(logs), "count": len(logs)},
            )

        if action == "clear_console_logs":
            await session.console_handler.clear_logs()
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
            )

        # ========== 截图 ==========

        if action == "screenshot":
            full_page = kwargs.get("full_page", False)
            selector = kwargs.get("selector")
            scale = kwargs.get("scale", 1.0)
            quality = kwargs.get("quality")
            timeout = kwargs.get("timeout", 30000)
            try:
                screenshot_data = await session.screenshot(
                    full_page=full_page,
                    selector=selector,
                    scale=scale,
                    quality=quality,
                    timeout=timeout,
                )
            except Exception as e:
                raise ScreenshotError(f"Screenshot failed: {e}") from e
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"screenshot": screenshot_data},
            )

        # ========== JavaScript 执行 ==========

        if action == "evaluate":
            expression = kwargs.get("expression")
            if not expression:
                raise InvalidActionError("expression is required for evaluate action")
            result = await session.evaluate(expression)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"result": result},
            )

        if action == "wait_for_selector":
            selector = kwargs.get("selector")
            if not selector:
                raise InvalidActionError("selector is required for wait_for_selector action")
            timeout = kwargs.get("timeout", 30000)
            state = kwargs.get("state", "visible")
            await session.wait_for_selector(selector, timeout=timeout, state=state)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
                data={"selector": selector},
            )

        if action == "wait_for_load_state":
            state = kwargs.get("state", "load")
            timeout = kwargs.get("timeout", 30000)
            await session.wait_for_load_state(state=state, timeout=timeout)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            return create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
            )

        # 无效的 action
        raise InvalidActionError(f"Unknown action: {action}")

    except WebDevError as e:
        error_msg = f"{e!s}"
        logger.info(f"RESPONSE - FAILED - action={action}, error={error_msg}")
        return create_web_dev_result(
            success=False,
            action=action,
            session_id=session_id,
            error=error_msg,
        )
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e!s}"
        logger.error(f"RESPONSE - FAILED - action={action}, error={error_msg}")
        return create_web_dev_result(
            success=False,
            action=action,
            session_id=session_id,
            error=error_msg,
        )
