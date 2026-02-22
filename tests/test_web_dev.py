"""Web-Dev 工具集成测试。"""

import json
import socketserver
import threading
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

import pytest
from fastmcp import Client


# ============================================================================
# 本地 HTTP 服务器
# ============================================================================


class TestHTTPHandler(SimpleHTTPRequestHandler):
    """测试用 HTTP 请求处理器。"""

    def __init__(self, *args, **kwargs):
        directory = Path(__file__).parent / "test_web_dev_files"
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, fmt, *args):
        """禁止输出日志。"""
        pass


@pytest.fixture(scope="module")
def http_server():
    """启动本地 HTTP 服务器。"""
    port = 8888
    handler = TestHTTPHandler

    # 尝试启动服务器
    server = None
    for attempt in range(3):
        try:
            server = socketserver.TCPServer(("", port), handler)
            break
        except OSError:
            port += 1

    if not server:
        raise RuntimeError("无法启动测试 HTTP 服务器")

    # 在后台线程运行服务器
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    yield f"http://localhost:{server.server_address[1]}"

    # 关闭服务器
    server.shutdown()
    server.server_close()


# ============================================================================
# MCP 客户端相关
# ============================================================================


@pytest.fixture
async def mcp_client():
    """启动 MCP 服务器并返回客户端实例。"""
    server_path = Path("mcp_stdio.py")
    client = Client(server_path)

    try:
        async with client:
            yield client
    finally:
        pass


# ============================================================================
# MCP 工具测试
# ============================================================================


# ============================================================================
# 测试辅助函数
# ============================================================================

async def _create_session(mcp_client) -> str:
    """创建会话并返回 session_id。"""
    result = await mcp_client.call_tool(
        "web_dev",
        {"action": "create_session"},
    )
    result_data = json.loads(result.content[0].text)
    assert result_data["success"] is True
    return result_data["session_id"]


async def _navigate_to_url(mcp_client, session_id: str, url: str):
    """导航到指定 URL。"""
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "navigate",
            "session_id": session_id,
            "action_data": json.dumps({"url": url, "timeout": 20000}),
        },
    )
    result_data = json.loads(result.content[0].text)
    assert result_data["success"] is True


async def _verify_page_info(mcp_client, session_id: str):
    """验证页面信息。"""
    result = await mcp_client.call_tool(
        "web_dev",
        {"action": "get_page_info", "session_id": session_id},
    )
    result_data = json.loads(result.content[0].text)
    assert result_data["success"] is True
    assert "Web Dev Test Page" in result_data["data"]["page"]["title"]


async def _test_element_operations(mcp_client, session_id: str):
    """测试元素操作：click, fill, clear, select_option, check, uncheck, hover。"""
    # 测试点击
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "click",
            "session_id": session_id,
            "action_data": json.dumps({"selector": "#click-btn"}),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True

    # 测试 fill 填充输入框
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "fill",
            "session_id": session_id,
            "action_data": json.dumps({"selector": "#text-input", "value": "测试文本"}),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True

    # 测试 clear 清空
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "clear",
            "session_id": session_id,
            "action_data": json.dumps({"selector": "#text-input"}),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True

    # 测试 select_option 下拉选择
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "select_option",
            "session_id": session_id,
            "action_data": json.dumps({"selector": "#select-dropdown", "values": ["option2"]}),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True

    # 测试 check 勾选复选框
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "check",
            "session_id": session_id,
            "action_data": json.dumps({"selector": "#check1"}),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True

    # 测试 uncheck 取消勾选
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "uncheck",
            "session_id": session_id,
            "action_data": json.dumps({"selector": "#check2"}),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True

    # 测试 hover 悬停
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "hover",
            "session_id": session_id,
            "action_data": json.dumps({"selector": "#hover-box"}),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True


async def _test_drag_and_drop(mcp_client, session_id: str):
    """测试拖放操作。"""
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "drag_and_drop",
            "session_id": session_id,
            "action_data": json.dumps({
                "source_selector": "#drag-source",
                "target_selector": "#drop-target",
            }),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True


async def _test_keyboard_mouse(mcp_client, session_id: str):
    """测试键盘和鼠标操作：press_key, scroll。"""
    # 测试 press_key 按键
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "press_key",
            "session_id": session_id,
            "action_data": json.dumps({"key": "Tab"}),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True

    # 测试 scroll 滚动
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "scroll",
            "session_id": session_id,
            "action_data": json.dumps({"y": 200}),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True


async def _test_query_operations(mcp_client, session_id: str):
    """测试查询操作：get_element_info, search_elements。"""
    # 测试 get_element_info - 使用 h1 标签选择器
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "get_element_info",
            "session_id": session_id,
            "action_data": json.dumps({"selector": "h1"}),
        },
    )
    result_data = json.loads(result.content[0].text)
    if not result_data["success"]:
        print(f"get_element_info error: {result_data.get('error')}")
    assert result_data["success"] is True
    assert "element" in result_data["data"]

    # 测试 search_elements
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "search_elements",
            "session_id": session_id,
            "action_data": json.dumps({"selector": "button"}),
        },
    )
    result_data = json.loads(result.content[0].text)
    if not result_data["success"]:
        print(f"search_elements error: {result_data.get('error')}")
    assert result_data["success"] is True
    assert "elements" in result_data["data"]
    assert result_data["data"]["count"] > 0


async def _test_console_logs(mcp_client, session_id: str):
    """测试 Console 日志操作：get_console_logs, clear_console_logs。"""
    # 测试 get_console_logs
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "get_console_logs",
            "session_id": session_id,
            "action_data": json.dumps({"type": "log", "limit": 10}),
        },
    )
    result_data = json.loads(result.content[0].text)
    assert result_data["success"] is True
    assert "logs" in result_data["data"]

    # 测试 clear_console_logs
    result = await mcp_client.call_tool(
        "web_dev",
        {"action": "clear_console_logs", "session_id": session_id},
    )
    assert json.loads(result.content[0].text)["success"] is True


async def _test_javascript_operations(mcp_client, session_id: str):
    """测试 JavaScript 操作：wait_for_selector。"""
    # 测试 wait_for_selector
    result = await mcp_client.call_tool(
        "web_dev",
        {
            "action": "wait_for_selector",
            "session_id": session_id,
            "action_data": json.dumps({"selector": "#page-title", "state": "visible"}),
        },
    )
    assert json.loads(result.content[0].text)["success"] is True


async def _close_session(mcp_client, session_id: str):
    """关闭会话。"""
    result = await mcp_client.call_tool(
        "web_dev",
        {"action": "close_session", "session_id": session_id},
    )
    assert json.loads(result.content[0].text)["success"] is True


# ============================================================================
# 主测试函数
# ============================================================================

@pytest.mark.asyncio
async def test_web_dev_all_action(mcp_client, http_server):
    """测试所有 web_dev action 的完整流程。"""
    test_url = f"{http_server}/test.html"

    # 1. 创建会话
    session_id = await _create_session(mcp_client)

    # 2. 导航到测试 URL
    await _navigate_to_url(mcp_client, session_id, test_url)

    # 3. 获取页面信息验证导航成功
    await _verify_page_info(mcp_client, session_id)

    # 4. 测试所有支持的 action
    await _test_element_operations(mcp_client, session_id)
    await _test_drag_and_drop(mcp_client, session_id)
    await _test_keyboard_mouse(mcp_client, session_id)

    # 再次导航回测试页面
    await _navigate_to_url(mcp_client, session_id, test_url)

    await _test_query_operations(mcp_client, session_id)
    await _test_console_logs(mcp_client, session_id)
    await _test_javascript_operations(mcp_client, session_id)

    # 5. 关闭会话
    await _close_session(mcp_client, session_id)
