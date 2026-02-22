"""调试会话 - 封装单个浏览器页面的调试会话。"""

import asyncio
import base64
from dataclasses import dataclass
from typing import Any
from pathlib import Path

from playwright.async_api import Page, Keyboard, Mouse

from web_dev.console_handler import ConsoleHandler


@dataclass
class ElementInfo:
    """元素信息。"""

    tag_name: str | None = None
    id: str | None = None
    classes: list[str] | None = None
    text: str | None = None
    inner_html: str | None = None
    attributes: dict[str, str] | None = None
    bounding_box: dict[str, float] | None = None
    css_style: dict[str, str] | None = None
    visible: bool = False
    enabled: bool = False


@dataclass
class PageInfo:
    """页面信息。"""

    url: str
    title: str
    viewport_size: dict[str, int] | None
    user_agent: str | None
    cookies: list[dict[str, Any]] | None


class DevSession:
    """单个调试会话。"""

    def __init__(self, session_id: str, page: Page):
        self._session_id = session_id
        self._page = page
        self._console_handler = ConsoleHandler()
        self._attached = False
        self._setup_listeners()

    @property
    def session_id(self) -> str:
        """获取会话 ID。"""
        return self._session_id

    @property
    def page(self) -> Page:
        """获取页面对象。"""
        return self._page

    @property
    def console_handler(self) -> ConsoleHandler:
        """获取 Console 处理器。"""
        return self._console_handler

    def _setup_listeners(self) -> None:
        """设置事件监听器。"""

        async def on_console(message):
            """处理 console 事件。"""
            msg_type = message.type
            text = message.text
            location = message.location.get("url", "") if message.location else None
            stack = None

            # 获取消息参数
            args = []
            for arg in message.args:
                try:
                    arg_value = await arg.json_value()
                    args.append(str(arg_value))
                except Exception:
                    pass

            if args:
                text = " ".join(args)

            await self._console_handler.add_log(
                log_type=msg_type,
                message=text,
                location=location,
            )

        async def on_pageerror(error):
            """处理页面错误事件。"""
            await self._console_handler.add_log(
                log_type="pageerror",
                message=str(error),
                stack=getattr(error, "stack", None),
            )

        self._page.on("console", on_console)
        self._page.on("pageerror", on_pageerror)
        self._attached = True

    async def cleanup(self) -> None:
        """清理资源。"""
        if self._attached:
            try:
                self._page.remove_listener("console")
                self._page.remove_listener("pageerror")
            except Exception:
                pass
            self._attached = False

    # ========== 导航操作 ==========

    async def navigate(self, url: str, timeout: float = 30000, wait_until: str = "load") -> None:
        """导航到指定 URL。

        Args:
            url: 目标 URL
            timeout: 超时时间（毫秒）
            wait_until: 等待事件 ("load", "domcontentloaded", "networkidle", "commit")
        """
        await self._page.goto(url, timeout=timeout, wait_until=wait_until)

    async def go_back(self) -> None:
        """后退。"""
        await self._page.go_back()

    async def go_forward(self) -> None:
        """前进。"""
        await self._page.go_forward()

    async def reload(self) -> None:
        """刷新页面。"""
        await self._page.reload()

    # ========== 元素操作 ==========

    async def click(
        self,
        selector: str,
        timeout: float = 30000,
        force: bool = False,
        no_wait_after: bool = False,
    ) -> None:
        """点击元素。

        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            force: 是否强制点击
            no_wait_after: 是否不等待导航
        """
        await self._page.click(
            selector,
            timeout=timeout,
            force=force,
            no_wait_after=no_wait_after,
        )

    async def fill(
        self,
        selector: str,
        value: str,
        timeout: float = 30000,
    ) -> None:
        """填充输入框。

        Args:
            selector: 输入框选择器
            value: 要填充的值
            timeout: 超时时间（毫秒）
        """
        await self._page.fill(selector, value, timeout=timeout)

    async def type_text(
        self,
        selector: str,
        text: str,
        delay: float = 0,
        timeout: float = 30000,
    ) -> None:
        """逐个字符输入文本。

        Args:
            selector: 输入框选择器
            text: 要输入的文本
            delay: 每个字符输入的延迟（毫秒）
            timeout: 超时时间（毫秒）
        """
        await self._page.type(selector, text, delay=delay, timeout=timeout)

    async def clear(self, selector: str, timeout: float = 30000) -> None:
        """清空输入框。

        Args:
            selector: 输入框选择器
            timeout: 超时时间（毫秒）
        """
        await self._page.fill(selector, "", timeout=timeout)

    async def select_option(
        self,
        selector: str,
        values: str | list[str] | None = None,
        labels: str | list[str] | None = None,
        timeout: float = 30000,
    ) -> None:
        """选择下拉选项。

        Args:
            selector: 选择器选择器
            values: 按值选择
            labels: 按标签选择
            timeout: 超时时间（毫秒）
        """
        await self._page.select_option(
            selector,
            value=values,
            label=labels,
            timeout=timeout,
        )

    async def check(self, selector: str, timeout: float = 30000) -> None:
        """勾选复选框。

        Args:
            selector: 复选框选择器
            timeout: 超时时间（毫秒）
        """
        await self._page.check(selector, timeout=timeout)

    async def uncheck(self, selector: str, timeout: float = 30000) -> None:
        """取消勾选复选框。

        Args:
            selector: 复选框选择器
            timeout: 超时时间（毫秒）
        """
        await self._page.uncheck(selector, timeout=timeout)

    async def hover(self, selector: str, timeout: float = 30000) -> None:
        """鼠标悬停在元素上。

        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        await self._page.hover(selector, timeout=timeout)

    async def drag_and_drop(
        self,
        source_selector: str,
        target_selector: str,
        timeout: float = 30000,
    ) -> None:
        """拖放操作。

        Args:
            source_selector: 源元素选择器
            target_selector: 目标元素选择器
            timeout: 超时时间（毫秒）
        """
        await self._page.drag_and_drop(
            source_selector,
            target_selector,
            timeout=timeout,
        )

    async def focus(self, selector: str, timeout: float = 30000) -> None:
        """聚焦元素。

        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        await self._page.focus(selector, timeout=timeout)

    # ========== 键盘和鼠标操作 ==========

    @property
    def keyboard(self) -> Keyboard:
        """获取键盘操作对象。"""
        return self._page.keyboard

    @property
    def mouse(self) -> Mouse:
        """获取鼠标操作对象。"""
        return self._page.mouse

    async def press_key(
        self,
        key: str,
        delay: float = 0,
    ) -> None:
        """按下键盘按键。

        Args:
            key: 按键名称（如 "Enter", "Escape", "ArrowDown"）
            delay: 延迟时间（毫秒）
        """
        await self._page.keyboard.press(key, delay=delay)

    async def scroll(
        self,
        x: float | None = None,
        y: float | None = None,
    ) -> None:
        """滚动页面。

        Args:
            x: 水平滚动位置
            y: 垂直滚动位置
        """
        if x is not None and y is not None:
            await self._page.evaluate(f"window.scrollTo({x}, {y})")
        elif y is not None:
            await self._page.evaluate(f"window.scrollTo(0, {y})")
        elif x is not None:
            await self._page.evaluate(f"window.scrollTo({x}, 0)")

    # ========== 查询操作 ==========

    async def get_element_info(
        self,
        selector: str,
        timeout: float = 30000,
    ) -> ElementInfo:
        """获取元素信息。

        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）

        Returns:
            元素信息对象
        """
        element = await self._page.wait_for_selector(selector, timeout=timeout)
        if not element:
            return ElementInfo()

        info = ElementInfo()

        # 获取标签名
        info.tag_name = await element.evaluate("el => el.tagName?.toLowerCase()")

        # 获取 ID
        info.id = await element.evaluate("el => el.id")

        # 获取 class 列表
        classes_str = await element.evaluate("el => el.className")
        if classes_str:
            info.classes = classes_str.split()

        # 获取文本内容
        try:
            info.text = await element.text_content()
        except Exception:
            pass

        # 获取 innerHTML
        try:
            info.inner_html = await element.inner_html()
        except Exception:
            pass

        # 获取属性
        try:
            attributes = await element.evaluate("""el => {
                const attrs = {};
                for (const attr of el.attributes) {
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            }""")
            info.attributes = attributes
        except Exception:
            info.attributes = {}

        # 获取 bounding box
        try:
            box = await element.bounding_box()
            if box:
                info.bounding_box = {
                    "x": box.x,
                    "y": box.y,
                    "width": box.width,
                    "height": box.height,
                }
        except Exception:
            pass

        # 获取 CSS 样式
        try:
            style = await element.evaluate("""el => {
                const style = window.getComputedStyle(el);
                const computed = {};
                for (let i = 0; i < style.length; i++) {
                    const prop = style[i];
                    computed[prop] = style.getPropertyValue(prop);
                }
                return computed;
            }""")
            info.css_style = style
        except Exception:
            info.css_style = {}

        # 检查是否可见
        try:
            info.visible = await element.is_visible()
        except Exception:
            info.visible = False

        # 检查是否启用
        try:
            info.enabled = await element.is_enabled()
        except Exception:
            info.enabled = False

        return info

    async def get_page_info(self) -> PageInfo:
        """获取页面信息。

        Returns:
            页面信息对象
        """
        viewport = self._page.viewport_size
        viewport_size = None
        if viewport:
            viewport_size = {
                "width": viewport.width,
                "height": viewport.height,
            }

        cookies = await self._page.context.cookies(self._page.url) if self._page.context else None

        return PageInfo(
            url=self._page.url,
            title=await self._page.title(),
            viewport_size=viewport_size,
            user_agent=await self._page.evaluate("() => navigator.userAgent"),
            cookies=cookies,
        )

    async def search_elements(
        self,
        selector: str,
        timeout: float = 5000,
    ) -> list[dict[str, Any]]:
        """搜索元素。

        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）

        Returns:
            元素信息列表
        """
        try:
            elements = await self._page.query_selector_all(selector)
            results = []

            for i, element in enumerate(elements):
                tag_name = await element.evaluate("el => el.tagName?.toLowerCase()")
                text = await element.text_content()
                element_id = await element.evaluate("el => el.id")
                class_name = await element.evaluate("el => el.className")

                results.append({
                    "index": i,
                    "tag_name": tag_name,
                    "id": element_id,
                    "class": class_name,
                    "text": (text or "").strip()[:100],
                })

            return results
        except Exception:
            return []

    # ========== 截图操作 ==========

    async def screenshot(
        self,
        full_page: bool = False,
        selector: str | None = None,
        scale: float = 1.0,
        quality: int | None = None,
        timeout: float = 30000,
    ) -> str:
        """截图并返回 base64 编码的图片数据。

        Args:
            full_page: 是否截取整个页面
            selector: 元素选择器（如果指定则只截取该元素）
            scale: 缩放比例
            quality: 图片质量（0-100，仅对 JPEG 有效）
            timeout: 超时时间（毫秒）

        Returns:
            base64 编码的图片数据（带 data URL 前缀）
        """
        screenshot_kwargs = {
            "full_page": full_page,
            "scale": scale,
            "timeout": timeout,
        }

        if quality:
            screenshot_kwargs["quality"] = quality

        if selector:
            element = await self._page.wait_for_selector(selector, timeout=timeout)
            if not element:
                raise ValueError(f"Element not found: {selector}")
            screenshot_bytes = await element.screenshot(**screenshot_kwargs)
        else:
            screenshot_bytes = await self._page.screenshot(**screenshot_kwargs)

        # 转换为 base64
        base64_data = base64.b64encode(screenshot_bytes).decode("utf-8")
        return f"data:image/png;base64,{base64_data}"

    # ========== JavaScript 执行 ==========

    async def evaluate(self, expression: str, **kwargs: Any) -> Any:
        """执行 JavaScript 表达式。

        Args:
            expression: JavaScript 表达式
            **kwargs: 传递给 JavaScript 的参数

        Returns:
            执行结果
        """
        return await self._page.evaluate(expression, kwargs)

    async def wait_for_selector(
        self,
        selector: str,
        timeout: float = 30000,
        state: str = "visible",
    ) -> None:
        """等待元素出现。

        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            state: 等待状态 ("attached", "detached", "visible", "hidden")
        """
        await self._page.wait_for_selector(selector, timeout=timeout, state=state)

    async def wait_for_load_state(
        self,
        state: str = "load",
        timeout: float = 30000,
    ) -> None:
        """等待页面加载状态。

        Args:
            state: 加载状态 ("load", "domcontentloaded", "networkidle")
            timeout: 超时时间（毫秒）
        """
        await self._page.wait_for_load_state(state, timeout=timeout)
