# Web-MCP Server

一个 Model Context Protocol (MCP) 服务器，提供 Web 搜索、Web 读取和网页开发调试功能。

## 功能特性

### Web 开发调试 (Web-Dev)

- **会话管理**：创建/关闭/列出多个调试会话，支持并发调试
- **网页操作**：导航、点击、输入、下拉选择、勾选、鼠标悬停、拖放等
- **键盘/鼠标操作**：按键输入、页面滚动、键盘和鼠标直接控制
- **元素查询**：获取元素信息（位置、大小、CSS样式、属性等）、搜索元素
- **Console 日志**：实时捕获 console 日志和 JavaScript 异常
- **截图功能**：页面截图、元素截图，支持全页截图和指定元素截图
- **JavaScript 执行**：直接在页面执行 JavaScript 代码
- **智能等待**：等待元素出现、等待页面加载状态

### Web 读取

- **智能内容提取**：使用 Mozilla Readability.js 算法提取网页正文内容
- **Markdown 转换**：将 HTML 自动转换为格式化的 Markdown
- **智能摘要**：自动提取页面描述或生成摘要
- **元数据提取**：提取标题、作者、字数统计、站点名称等
- **Playwright 浏览器**：使用真实浏览器加载网页，兼容性更好
- **国际化支持**：完整支持中英文内容

### Web 搜索

- **Bing 搜索**：使用 Playwright 访问 Bing.com 进行真实搜索
- **无需 API Key**：直接通过浏览器获取搜索结果，无需申请 API 密钥
- **结果排序**：按相关性返回搜索结果
- **摘要预览**：提供搜索结果摘要
- **支持翻页**：可获取更多搜索结果（默认 10 条，最多 50 条）

## 安装

```bash
# 使用 uv 安装
uv sync
```

### 配置环境变量（可选）

复制 `.env.example` 为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

支持的配置项：

- **MCP_SERVER_PORT**: SSE 模式服务器端口（默认：8000）
- **BROWSER_HEADLESS**: 是否使用无头模式（默认：false）
- **BROWSER_MAX_CACHED_PAGES**: 最大缓存页面数量（默认：10）
- **BROWSER_INITIAL_PAGE_COUNT**: 初始页面数量（默认：1）
- **BROWSER_VIEWPORT_WIDTH**: 浏览器视口宽度（默认：1280）
- **BROWSER_VIEWPORT_HEIGHT**: 浏览器视口高度（默认：720）

详细配置说明请参考 `.env.example` 文件。

### 依赖要求

- **系统要求**：
    - Python >= 3.11

- **Python 依赖**：
    - markdownify >= 0.13.1
    - beautifulsoup4 >= 4.12.0
    - fastmcp == 3.0.1
    - types-beautifulsoup4 >= 4.12.0.20250516
    - python-dotenv >= 1.0.0
    - playwright >= 1.58.0

**首次使用需要安装以下组件**：

```bash
# 安装 Playwright 浏览器（用于 Web 搜索和 Web 读取）
uv run playwright install chromium
```

## 使用方法

### 配置客户端

Web-MCP 支持两种传输模式：**HTTP**（推荐，本机使用）和 **stdio**（本地使用）。

#### 方式一：HTTP 传输（推荐，本机使用）

首先启动 HTTP 服务器：

```bash
# 启动 HTTP 服务器（默认监听 http://localhost:8000）
uv run mcp_http.py

```

然后在 MCP 客户端的配置文件中添加：

```json
{
  "mcpServers": {
    "web-mcp": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**推荐理由**：

- 可以通过浏览器窗口直观看到搜索和页面加载过程
- 便于调试和排查问题
- 配置简单，无需路径配置
- 多开窗口可以共用一个浏览器实例，避免重复加载
- 无头模式容易被网站屏蔽

#### 方式二：stdio 传输（本地使用）

在 MCP 客户端的配置文件中添加：

```json
{
  "mcpServers": {
    "web-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/web-mcp",
        "mcp_stdio.py"
      ]
    }
  }
}
```

**注意**: 将 `/path/to/web-mcp` 替换为项目的实际路径。

### 可用工具

web-mcp 提供以下三个工具：

#### 1. web_dev

网页开发调试工具 - 单一综合入口，通过 `action` 参数区分不同操作。

| 参数           | 类型      | 必填 | 默认值   | 描述                 |
|--------------|---------|----|-------|--------------------|
| `action`     | string  | ✅  | -     | 操作类型，见下方支持的 action 列表 |
| `session_id` | string  | ❌  | -     | 会话 ID（除 create_session 外都需要） |
| `**kwargs`   | any     | ❌  | -     | 具体操作的参数          |

**支持的 Action**：

- **会话管理**：`create_session`, `close_session`, `list_sessions`
- **导航操作**：`navigate`, `go_back`, `go_forward`, `reload`
- **元素操作**：`click`, `fill`, `type_text`, `clear`, `select_option`, `check`, `uncheck`, `hover`, `drag_and_drop`, `focus`
- **键盘鼠标**：`press_key`, `scroll`
- **查询操作**：`get_element_info`, `get_page_info`, `search_elements`
- **Console 日志**：`get_console_logs`, `clear_console_logs`
- **截图**：`screenshot`
- **JavaScript**：`evaluate`, `wait_for_selector`, `wait_for_load_state`

详细使用说明请参考 `docs/module/WEB_DEV.md`。

#### 2. web_search

执行 Web 搜索并返回结果。

使用 Playwright 访问 Bing 搜索，无需 API Key。

| 参数            | 类型     | 必填 | 默认值  | 描述             |
|---------------|--------|----|------|----------------|
| `query`       | string | ✅  | -    | 搜索关键词          |
| `num_results` | int    | ❌  | `10` | 返回结果数量，范围 1-50 |

#### 3. url_fetcher

读取网页并转换为 Markdown 或纯文本格式。

使用 **Playwright + Readability.js** 进行智能内容提取。

| 参数              | 类型      | 必填 | 默认值        | 描述                                    |
|-----------------|---------|----|------------|---------------------------------------|
| `url`           | string  | ✅  | -          | 要读取的网页 URL（必须以 http:// 或 https:// 开头） |
| `return_format` | string  | ❌  | `markdown` | 返回格式：`markdown` 或 `text`              |
| `timeout`       | integer | ❌  | `20`       | 请求超时时间（秒），范围 5-60                     |

**关于内容提取**：

- 使用 Mozilla Readability.js 算法，提取准确率高，能更好地处理复杂网页结构
- Readability.js 脚本位置：`res/Readability.js`

### 使用示例

配置完成后，在支持 MCP 的客户端中可以直接调用工具：

**Web 搜索示例**：

```
请帮我搜索"Python 异步编程教程"
```

MCP 客户端会自动调用 `web_search` 工具并返回搜索结果。

**Web 读取示例**：

```
请帮我读取 https://example.com/article 的内容
```

MCP 客户端会自动调用 `url_fetcher` 工具并返回网页内容。

### 返回格式

#### web_search 返回格式

成功时的返回示例：

```json
{
  "success": true,
  "query": "Python 异步编程",
  "results": [
    {
      "title": "Python 异步编程完整指南",
      "url": "https://example.com/async-python",
      "snippet": "详细介绍 Python 中的 async/await 语法...",
      "rank": 1
    }
  ],
  "total_results": 10
}
```

#### url_fetcher 返回格式

成功时的返回示例：

```json
{
  "success": true,
  "url": "https://example.com/article",
  "title": "文章标题",
  "summary": "文章摘要...",
  "content": "# 文章标题\n\n正文内容...",
  "metadata": {
    "author": "作者名称",
    "word_count": 1234,
    "site_name": "网站名称"
  }
}
```

失败时的返回示例：

```json
{
  "success": false,
  "url": "https://example.com/article",
  "error": "获取错误：获取 https://example.com/article 时超时"
}
```

## 开发

### 运行测试

```bash
# 安装开发依赖
uv sync --extra dev

# 运行测试
uv run pytest

# 运行测试并查看覆盖率
uv run pytest --cov=url_fetcher --cov=web_search --cov-report=html
```
