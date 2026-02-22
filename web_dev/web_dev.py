"""Web-Dev 工具函数 - 提供 MCP 工具接口。"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from web_dev.config import WebDevConfig
from web_dev.console_handler import ConsoleLog
from web_dev.dev_session import ElementInfo, PageInfo
from web_dev.exceptions import (
    WebDevError,
    InvalidActionError,
    NavigationError,
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


def _parse_action_data(action_data: str | None) -> dict[str, Any]:
    """解析 action_data JSON 字符串。"""
    if not action_data:
        return {}
    try:
        return json.loads(action_data)
    except json.JSONDecodeError as e:
        raise InvalidActionError(f"Invalid action_data JSON: {e}")


async def web_dev(
        action: str,
        session_id: str | None = None,
        action_data: str | None = None,
        delay: int = 1000,
        timeout: int = 30000,
) -> str:
    """网页开发调试工具。

    操作流程: create_session(获取session_id) -> 各种操作(带session_id) -> close_session

    Args:
        action: 操作类型:
        session_id: 会话ID（除create_session外都需要）
        action_data: JSON字符串，包含操作参数(根据操作类型不同而不同)
        delay: 执行后等待毫秒数，默认1000（会话操作忽略）
        timeout: 操作超时毫秒数，默认30000
    操作类型说明:
        - 会话管理:
            create_session: 创建新会话，返回session_id
            close_session: 关闭指定会话
        - 导航操作:
            navigate: 跳转到URL，action_data: {url}
        - 元素操作 (action_data需含selector):
            click: 点击元素
            fill: 填充输入框，需: value
            clear: 清空输入框
            select_option: 下拉选择，需: values或labels
            check: 勾选复选框
            uncheck: 取消勾选
            hover: 鼠标悬停
            drag_and_drop: 拖放，需: source_selector, target_selector
        - 键盘鼠标:
            press_key: 按键，action_data: {key}
            scroll: 滚动，action_data: {x或y}
        - 查询操作:
            get_element_info: 获取元素信息，action_data: {selector}
            get_page_info: 获取页面信息
            search_elements: 搜索元素，action_data: {selector}
        - Console日志:
            get_console_logs: 获取日志，action_data可选: {type, limit}
            clear_console_logs: 清空日志
        - JavaScript:
            wait_for_selector: 等待元素，action_data: {selector, state="visible"}
    Returns:
        JSON格式结果 {success, action, session_id, data, error}
    """
    logger.info(f"REQUEST - action={action}, session_id={session_id}, delay={delay}, timeout={timeout}")

    # 判断是否需要执行 delay（会话管理 action 忽略）
    need_delay = action not in {"create_session", "close_session"}

    try:
        params = _parse_action_data(action_data)
        manager = await get_session_manager()

        # ========== 会话管理 ==========

        if action == "create_session":
            new_session_id = await manager.create_session()
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={new_session_id}")
            result = create_web_dev_result(
                success=True,
                action=action,
                session_id=new_session_id,
                data={"session_id": new_session_id},
            )

        # 以下操作都需要 session_id
        elif not session_id:
            raise InvalidActionError("session_id is required for this action")

        elif action == "close_session":
            await manager.close_session(session_id)
            logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
            result = create_web_dev_result(
                success=True,
                action=action,
                session_id=session_id,
            )

        else:
            # 获取会话
            session = manager.get_session(session_id)

            # ========== 导航操作 ==========

            if action == "navigate":
                url = params.get("url")
                if not url:
                    raise InvalidActionError("url is required for navigate action")
                try:
                    await session.navigate(url, timeout=timeout)
                except Exception as e:
                    raise NavigationError(f"Navigation failed: {e}") from e
                # 更新会话信息
                page_info = await session.get_page_info()
                manager.update_session_info(session_id, url=page_info.url, title=page_info.title)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, url={url}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"url": url},
                )

            # ========== 元素操作 ==========

            elif action == "click":
                selector = params.get("selector")
                if not selector:
                    raise InvalidActionError("selector is required for click action")
                await session.click(
                    selector,
                    timeout=timeout,
                )
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"selector": selector},
                )

            elif action == "fill":
                selector = params.get("selector")
                value = params.get("value")
                if not selector:
                    raise InvalidActionError("selector is required for fill action")
                if value is None:
                    raise InvalidActionError("value is required for fill action")
                await session.fill(selector, value, timeout=timeout)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"selector": selector},
                )

            elif action == "clear":
                selector = params.get("selector")
                if not selector:
                    raise InvalidActionError("selector is required for clear action")
                await session.clear(selector, timeout=timeout)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"selector": selector},
                )

            elif action == "select_option":
                selector = params.get("selector")
                if not selector:
                    raise InvalidActionError("selector is required for select_option action")
                values = params.get("values")
                labels = params.get("labels")
                if values is None and labels is None:
                    raise InvalidActionError("values or labels is required for select_option action")
                await session.select_option(
                    selector,
                    values=values,
                    labels=labels,
                    timeout=timeout,
                )
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"selector": selector},
                )

            elif action == "check":
                selector = params.get("selector")
                if not selector:
                    raise InvalidActionError("selector is required for check action")
                await session.check(selector, timeout=timeout)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"selector": selector},
                )

            elif action == "uncheck":
                selector = params.get("selector")
                if not selector:
                    raise InvalidActionError("selector is required for uncheck action")
                await session.uncheck(selector, timeout=timeout)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"selector": selector},
                )

            elif action == "hover":
                selector = params.get("selector")
                if not selector:
                    raise InvalidActionError("selector is required for hover action")
                await session.hover(selector, timeout=timeout)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"selector": selector},
                )

            elif action == "drag_and_drop":
                source_selector = params.get("source_selector")
                target_selector = params.get("target_selector")
                if not source_selector:
                    raise InvalidActionError("source_selector is required for drag_and_drop action")
                if not target_selector:
                    raise InvalidActionError("target_selector is required for drag_and_drop action")
                await session.drag_and_drop(
                    source_selector,
                    target_selector,
                    timeout=timeout,
                )
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={
                        "source_selector": source_selector,
                        "target_selector": target_selector,
                    },
                )

            # ========== 键盘和鼠标操作 ==========

            elif action == "press_key":
                key = params.get("key")
                if not key:
                    raise InvalidActionError("key is required for press_key action")
                await session.press_key(key, delay=delay)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, key={key}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"key": key},
                )

            elif action == "scroll":
                x = params.get("x")
                y = params.get("y")
                if x is None and y is None:
                    raise InvalidActionError("x or y is required for scroll action")
                await session.scroll(x=x, y=y)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"x": x, "y": y},
                )

            # ========== 查询操作 ==========

            elif action == "get_element_info":
                selector = params.get("selector")
                if not selector:
                    raise InvalidActionError("selector is required for get_element_info action")
                info = await session.get_element_info(selector, timeout=timeout)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"element": _serialize_element_info(info)},
                )

            elif action == "get_page_info":
                info = await session.get_page_info()
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"page": _serialize_page_info(info)},
                )

            elif action == "search_elements":
                selector = params.get("selector")
                if not selector:
                    raise InvalidActionError("selector is required for search_elements action")
                search_timeout = params.get("timeout", 5000)
                elements = await session.search_elements(selector, timeout=search_timeout)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, count={len(elements)}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"elements": elements, "count": len(elements)},
                )

            # ========== Console 日志 ==========

            elif action == "get_console_logs":
                log_type = params.get("type")
                limit = params.get("limit")
                logs = await session.console_handler.get_logs(
                    log_type=log_type,
                    limit=limit,
                )
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, count={len(logs)}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"logs": _serialize_console_logs(logs), "count": len(logs)},
                )

            elif action == "clear_console_logs":
                await session.console_handler.clear_logs()
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                )

            # ========== JavaScript 执行 ==========

            elif action == "wait_for_selector":
                selector = params.get("selector")
                if not selector:
                    raise InvalidActionError("selector is required for wait_for_selector action")
                state_val = params.get("state", "visible")
                await session.wait_for_selector(selector, timeout=timeout, state=state_val)
                logger.info(f"RESPONSE - SUCCESS - action={action}, session_id={session_id}, selector={selector}")
                result = create_web_dev_result(
                    success=True,
                    action=action,
                    session_id=session_id,
                    data={"selector": selector},
                )

            else:
                # 无效的 action
                raise InvalidActionError(f"Unknown action: {action}")

        # 执行 delay（如果需要）
        if need_delay and delay > 0:
            logger.debug(f"Action {action} completed, waiting {delay}ms")
            await asyncio.sleep(delay / 1000.0)

        return result

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
