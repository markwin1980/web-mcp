# Web-MCP Server

一个 Model Context Protocol (MCP) 服务器，提供 Web 搜索和 Web 读取功能。

## 功能特性

### Web 读取

- **智能内容提取**：使用 Readability 算法提取网页正文内容
- **Markdown 转换**：将 HTML 自动转换为格式化的 Markdown
- **智能摘要**：自动提取页面描述或生成摘要
- **元数据提取**：提取标题、作者、发布日期、Open Graph 信息等
- **内存缓存**：内置缓存机制，避免重复请求
- **国际化支持**：完整支持中英文内容

### Web 搜索

- **快速搜索**：支持多种搜索引擎
- **结果排序**：按相关性返回搜索结果
- **摘要预览**：提供搜索结果摘要
- **多语言支持**：支持中英文等多种语言

## 安装

```bash
# 使用 uv 安装
uv sync
```

### 依赖要求

- Python >= 3.11
- aiohttp >= 3.9.0
- markdownify >= 0.13.1
- readabilipy >= 0.2.0
- beautifulsoup4 >= 4.12.0
- pydantic >= 2.0.0
- mcp >= 1.1.3

## 使用方法

### MCP 服务器配置

web-mcp 是一个标准的 MCP 服务器，可以在任何支持 MCP 协议的客户端中使用。

#### 服务器参数

- **名称**: `web-mcp`
- **命令**: `python` 或 `uv run`
- **参数**:
    - `main.py` （如果使用 `python`）
    - 或 `python main.py` （如果使用 `uv run`）

#### 配置示例

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
        "main.py"
      ]
    }
  }
}
```

**注意**: 将 `/path/to/web-mcp` 替换为项目的实际路径。

### 可用工具

web-mcp 提供以下两个工具：

#### 1. web_search

执行 Web 搜索并返回结果。

| 参数            | 类型     | 必填 | 默认值     | 描述                    |
|---------------|--------|----|---------|-----------------------|
| `query`       | string | ✅  | -       | 搜索关键词                 |
| `num_results` | int    | ❌  | `10`    | 返回结果数量，范围 1-100       |
| `language`    | string | ❌  | `zh-cn` | 搜索语言（如 zh-cn、en-us 等） |

#### 2. webReader

读取网页并转换为 Markdown 或纯文本格式。

| 参数              | 类型      | 必填 | 默认值        | 描述                                    |
|-----------------|---------|----|------------|---------------------------------------|
| `url`           | string  | ✅  | -          | 要读取的网页 URL（必须以 http:// 或 https:// 开头） |
| `return_format` | string  | ❌  | `markdown` | 返回格式：`markdown` 或 `text`              |
| `retain_images` | boolean | ❌  | `true`     | 是否在输出中保留图片                            |
| `timeout`       | integer | ❌  | `20`       | 请求超时时间（秒），范围 5-60                     |
| `no_cache`      | boolean | ❌  | `false`    | 是否禁用缓存                                |

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

MCP 客户端会自动调用 `webReader` 工具并返回网页内容。

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

#### webReader 返回格式

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
    "publish_date": "2024-01-15T10:30:00Z",
    "word_count": 1234,
    "image_count": 5,
    "og_title": "Open Graph 标题",
    "og_description": "Open Graph 描述",
    "og_image": "https://example.com/image.jpg",
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
uv sync --dev

# 运行测试
uv run pytest

# 运行测试并查看覆盖率
uv run pytest --cov=web_reader --cov-report=html
```

