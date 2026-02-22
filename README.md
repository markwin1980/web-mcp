# Web-MCP Server

一个 Model Context Protocol (MCP) 服务器，提供 Web 搜索和 Web 读取功能。

## 功能特性

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

### 依赖要求

- **系统要求**：
    - Python >= 3.11

- **Python 依赖**：
    - markdownify >= 0.13.1
    - beautifulsoup4 >= 4.12.0
    - mcp >= 1.26.0
    - types-beautifulsoup4 >= 4.12.0.20250516
    - python-dotenv >= 1.0.0
    - playwright >= 1.58.0
    - playwright-stealth >= 2.0.2

**首次使用需要安装以下组件**：

```bash
# 安装 Playwright 浏览器（用于 Web 搜索和 Web 读取）
uv run playwright install chromium
```

## 使用方法

### 配置客户端

Web-MCP 支持两种传输模式：**stdio**（本地使用）和 **SSE**（远程/网络使用）。

#### 方式一：stdio 传输（本地使用）

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

#### 方式二：SSE 传输（远程/网络使用）

首先启动 SSE 服务器：

```bash
# 启动 SSE 服务器（默认监听 http://localhost:8000）
uv run mcp_sse.py

# 或指定端口和主机
uv run mcp_sse.py --port 3000 --host 0.0.0.0
```

然后在 MCP 客户端的配置文件中添加：

```json
{
  "mcpServers": {
    "web-mcp": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**注意**: 将 `/path/to/web-mcp` 替换为项目的实际路径。

### 可用工具

web-mcp 提供以下两个工具：

#### 1. web_search

执行 Web 搜索并返回结果。

使用 Playwright 访问 Bing 搜索，无需 API Key。

| 参数            | 类型     | 必填 | 默认值  | 描述             |
|---------------|--------|----|------|----------------|
| `query`       | string | ✅  | -    | 搜索关键词          |
| `num_results` | int    | ❌  | `10` | 返回结果数量，范围 1-50 |

#### 2. url_fetcher

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
