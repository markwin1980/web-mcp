"""Pytest 配置和 fixtures。"""

import asyncio
import json
import subprocess
import sys
from typing import Any

import pytest


# ============================================================================
# MCP 客户端相关 - 用于集成测试
# ============================================================================


class MCPClient:
    """模拟 MCP 客户端，通过 stdio 与服务器通信。"""

    def __init__(self, server_process: subprocess.Popen):
        """初始化 MCP 客户端。

        Args:
            server_process: 已启动的 MCP 服务器进程
        """
        self.process = server_process
        self.request_id = 0

    def _create_request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """创建 JSON-RPC 请求。

        Args:
            method: MCP 方法名
            params: 方法参数

        Returns:
            JSON-RPC 请求字典
        """
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        if params:
            request["params"] = params
        return request

    async def send_request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """发送请求并获取响应。

        Args:
            method: MCP 方法名
            params: 方法参数

        Returns:
            JSON-RPC 响应字典
        """
        # 创建请求
        request = self._create_request(method, params)

        # 发送请求到服务器的 stdin
        request_json = json.dumps(request, ensure_ascii=False) + "\n"
        self.process.stdin.write(request_json.encode())
        self.process.stdin.flush()

        # 从服务器的 stdout 读取响应
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("服务器未返回响应")

        response = json.loads(response_line.decode())

        # 检查是否有错误
        if "error" in response:
            raise RuntimeError(f"MCP 错误: {response['error']}")

        return response

    async def initialize(self) -> dict[str, Any]:
        """初始化 MCP 连接。

        Returns:
            初始化响应
        """
        return await self.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0",
                },
            },
        )

    async def list_tools(self) -> list[dict[str, Any]]:
        """列出所有可用工具。

        Returns:
            工具列表
        """
        response = await self.send_request("tools/list")
        return response.get("result", {}).get("tools", [])

    async def call_tool(
        self, name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """调用工具。

        Args:
            name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        response = await self.send_request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments,
            },
        )
        return response.get("result", {})

    def close(self):
        """关闭客户端连接。"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=5)


@pytest.fixture
async def mcp_client():
    """启动 MCP 服务器并返回客户端实例。

    这个 fixture 会：
    1. 启动 MCP 服务器进程（stdio 模式）
    2. 创建客户端连接
    3. 测试结束后自动关闭服务器
    """
    # 启动 MCP 服务器进程
    server_process = subprocess.Popen(
        [sys.executable, "-m", "mcp_stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
        bufsize=1,
    )

    # 创建客户端
    client = MCPClient(server_process)

    try:
        # 等待服务器启动
        await asyncio.sleep(1)

        # 初始化连接
        await client.initialize()

        yield client

    finally:
        # 清理资源
        client.close()
