# TEST.md

本文件包含项目的**测试方法**和**测试文件说明**，更新本文档只需要更新这2个部分。

## 测试方法

本项目使用 pytest 进行单元测试和集成测试。

```bash
# 使用 uv 运行所有测试
uv run pytest

# 运行所有测试并显示详细输出
uv run pytest -v

# 运行特定测试文件
uv run pytest tests/test_fetcher.py
uv run pytest tests/test_parser.py
uv run pytest tests/test_mcp_server.py
uv run pytest tests/test_web_search.py
uv run pytest tests/test_url_fetcher.py

# 运行特定测试用例
uv run pytest tests/test_web_search.py::test_call_web_search

# 查看测试覆盖率
uv run pytest --cov=url_fetcher --cov=web_search --cov=main

# 生成覆盖率 HTML 报告
uv run pytest --cov=url_fetcher --cov=web_search --cov=main --cov-report=html
```

## 测试文件说明

### `conftest.py` - Pytest 配置和共享 Fixtures

提供测试所需的共享 fixtures 和工具类：

### 单元测试 Fixtures

- `config` - 测试配置实例
- `fetcher` - 网页获取器实例
- `parser` - HTML 解析器实例
- `sample_html` - 完整的示例 HTML 文档（用于测试文章解析）
- `sample_html_simple` - 简单的示例 HTML 文档（用于基础测试）

### 集成测试 Fixtures

- `MCPClient` - MCP 客户端类，通过 stdio 协议与 MCP 服务器通信
    - 支持发送 JSON-RPC 请求
    - 自动处理请求/响应序列化
    - 提供初始化、工具列表、工具调用等方法
- `mcp_client` - MCP 服务器客户端 fixture
    - 自动启动 MCP 服务器进程（stdio 模式）
    - 初始化 MCP 连接
    - 测试结束后自动关闭服务器

### `test_mcp_server.py` - MCP 服务器元数据测试

测试 MCP 服务器的初始化、协议信息、工具列表等元数据：

- `test_server_initialization` - 验证服务器进程成功启动
- `test_list_tools` - 验证能列出所有注册的工具（web_search 和 url_fetcher）
- `test_tools_have_descriptions` - 验证所有工具都有描述
- `test_tools_have_input_schema` - 验证所有工具都有输入 schema
- `test_concurrent_tool_calls` - 测试并发调用工具的能力
- `test_mcp_protocol_version` - 验证 MCP 协议版本（2024-11-05）
- `test_server_info` - 验证服务器信息（名称、版本）
- `test_server_capabilities` - 验证服务器能力声明
- `test_server_instructions` - 验证服务器说明文档

**测试方式**: 通过 stdio 启动真实的 MCP 服务器进程，使用 JSON-RPC 协议进行通信

### `test_web_search.py` - Web-Search 工具测试

测试 web_search 工具的功能和参数处理：

- `test_web_search_tool_schema` - 验证工具的输入 schema（query、num_results、language）
- `test_call_web_search` - 测试基本搜索功能
- `test_call_web_search_invalid_params` - 测试无效参数处理（num_results 超出范围）
- `test_web_search_default_params` - 测试默认参数使用
- `test_web_search_empty_query` - 测试空查询字符串处理
- `test_web_search_minimum_results` - 测试返回最小数量结果（num_results=1）

**测试方式**: 通过 MCP 客户端调用工具，验证返回的 JSON 结果格式和内容

### `test_url_fetcher.py` - URL-Fetcher 工具测试

测试 url_fetcher 工具的功能和参数处理：

- `test_url_fetcher_tool_schema` - 验证工具的输入 schema（url、return_format、retain_images、timeout、no_cache）
- `test_call_url_fetcher_with_public_site` - 测试基本网页读取功能（使用 example.com）
- `test_call_url_fetcher_invalid_url` - 测试无效 URL 处理
- `test_url_fetcher_invalid_timeout` - 测试无效超时参数处理
- `test_url_fetcher_text_format` - 测试纯文本格式输出
- `test_url_fetcher_with_images` - 测试保留图片选项
- `test_url_fetcher_no_cache` - 测试禁用缓存选项
- `test_url_fetcher_default_params` - 测试默认参数使用

**测试方式**: 通过 MCP 客户端调用工具，验证返回的 JSON 结果格式和内容

### `test_fetcher.py` - 网页获取器单元测试

测试 WebFetcher 组件的功能：

- `test_validate_url_success` - 测试有效 URL 验证（http/https）
- `test_validate_url_failure` - 测试无效 URL 被拒绝
- `test_cache_store_and_retrieve` - 测试缓存存储和检索
- `test_cache_expiration` - 测试缓存过期机制
- `test_clear_cache` - 测试清空缓存
- `test_fetch_invalid_url` - 测试使用无效 URL 获取时抛出异常
- `test_fetch_with_cache` - 测试缓存功能

**测试方式**: 直接实例化 WebFetcher 类进行单元测试

### `test_parser.py` - HTML 解析器单元测试

测试 HTMLParser 组件的功能：

- `test_extract_title` - 测试从文章 JSON 中提取标题
- `test_extract_title_from_h1` - 测试从 h1 标签提取标题
- `test_extract_summary_from_meta` - 测试从 meta description 提取摘要
- `test_extract_summary_from_first_p` - 测试从第一段提取摘要
- `test_truncate_summary` - 测试摘要截断功能
- `test_html_to_markdown` - 测试 HTML 转 Markdown
- `test_html_to_text` - 测试 HTML 转纯文本
- `test_extract_metadata` - 测试元数据提取（作者、发布日期、字数等）
- `test_parse_full` - 测试完整解析流程（markdown 格式）
- `test_parse_with_text_format` - 测试使用 text 格式解析

**测试方式**: 直接实例化 HTMLParser 类进行单元测试
