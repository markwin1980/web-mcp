# TEST.md

本文件包含项目的测试命令说明。

## 安装依赖

```bash
# 安装开发依赖（包含 pytest、pytest-asyncio、pytest-cov）
uv sync --extra dev
```

## 测试覆盖率

```bash
# 运行所有测试
uv run pytest

# 运行所有测试并显示详细输出
uv run pytest -v

```

## 运行特定测试文件

### Browser-Service 单元测试

测试浏览器服务模块的功能：初始化、关闭、页面池管理、异常处理

```bash
uv run pytest tests/test_browser_service.py
```

### MCP 服务器集成测试

测试 MCP 服务器的初始化、协议信息、工具列表等元数据

```bash
# 运行所有 MCP 服务器测试
uv run pytest tests/test_mcp_server.py

# 运行特定测试用例
uv run pytest tests/test_mcp_server.py::test_server_initialization       # 验证服务器进程成功启动
uv run pytest tests/test_mcp_server.py::test_list_tools                 # 验证能列出所有注册的工具
uv run pytest tests/test_mcp_server.py::test_concurrent_tool_calls       # 测试并发调用工具
```

### Web-Search 工具测试

测试 web_search 工具的功能和参数处理

```bash
# 运行所有 Web-Search 测试
uv run pytest tests/test_web_search.py

# 运行特定测试用例
uv run pytest tests/test_web_search.py::test_call_web_search                # 测试基本搜索功能
uv run pytest tests/test_web_search.py::test_web_search_default_params      # 测试默认参数
uv run pytest tests/test_web_search.py::test_web_search_invalid_params      # 测试无效参数处理
uv run pytest tests/test_web_search.py::test_web_search_empty_query          # 测试空查询处理
```

### URL-Fetcher 工具测试

测试 url_fetcher 工具的功能和参数处理

```bash
# 运行所有 URL-Fetcher 测试
uv run pytest tests/test_url_fetcher.py

# 运行特定测试用例
uv run pytest tests/test_url_fetcher.py::test_call_url_fetcher_with_public_site  # 测试基本网页读取
uv run pytest tests/test_url_fetcher.py::test_url_fetcher_markdown_format        # 测试 Markdown 格式
uv run pytest tests/test_url_fetcher.py::test_url_fetcher_invalid_url            # 测试无效 URL 处理
uv run pytest tests/test_url_fetcher.py::test_url_fetcher_default_params         # 测试默认参数
```

**注意**: 测试使用 `TEST_URL` 常量配置测试网站（默认为 cnblogs.com），可在 `test_url_fetcher.py` 顶部修改
