# TEST.md

本文件仅包含项目的**测试命令**说明。

## 安装依赖

```bash
# 安装开发依赖（包含 pytest、pytest-asyncio、pytest-cov）
uv sync --extra dev

# 首次运行需要安装 Playwright 浏览器
uv run playwright install
```

## 运行所有测试

```bash
# 运行所有测试
uv run pytest

# 运行所有测试并显示详细输出
uv run pytest -v

```

## 运行特定测试

### Browser-Service 单元测试

测试浏览器服务模块的功能：初始化、关闭、页面池管理、异常处理

```bash
uv run pytest tests/test_browser_service.py
```

### MCP 服务器集成测试

测试 MCP 服务器的初始化、协议信息、工具列表等元数据

```bash
uv run pytest tests/test_mcp_server.py
```

### Web-Search 工具测试

测试 web_search 工具的功能：5条结果（单页）、20条结果（翻页）

```bash
uv run pytest tests/test_web_search.py
```

### URL-Fetcher 工具测试

测试 url_fetcher 工具的功能：markdown 格式输出、text 格式输出

```bash
uv run pytest tests/test_url_fetcher.py
```

### Web-Dev 工具测试

测试 web_dev 工具的完整功能：
- 会话管理：create_session, close_session
- 导航操作：navigate, get_page_info
- 元素操作：click, fill, clear, select_option, check, uncheck, hover, drag_and_drop
- 键盘鼠标：press_key, scroll
- 查询操作：get_element_info, search_elements
- Console 日志：get_console_logs, clear_console_logs
- JavaScript 操作：wait_for_selector

```bash
uv run pytest tests/test_web_dev.py
```

**注意**: 测试使用 `TEST_URL` 常量配置测试网站（默认为 cnblogs.com），可在 `test_url_fetcher.py` 顶部修改
