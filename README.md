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

- **百度智能云千帆 AI 搜索**：使用百度千帆 AI 搜索 API 进行高质量搜索
- **结果排序**：按相关性返回搜索结果
- **摘要预览**：提供搜索结果摘要
- **智能排序**：支持 rerank_score 和 authority_score 排序

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
- mcp >= 1.26.0

## 使用方法

### 运行模式

web-mcp 支持两种运行模式：

| 模式        | 入口文件           | 传输方式  | 适用场景              |
|-----------|----------------|-------|-------------------|
| **本地模式**  | `mcp_stdio.py` | stdio | 本地 Claude 桌面客户端使用 |
| **服务器模式** | `mcp_sse.py`   | SSE   | 远程服务器部署           |

### 本地模式配置

适合在本地机器上运行，无需进行复杂的服务端配置。

#### 配置客户端

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

### 服务器模式配置

配置成http服务的模式，可以共享使用。

#### 启动服务器

```bash
python mcp_sse.py
```

#### 环境变量配置

在服务器上创建 `.env` 文件：

```env
BAIDU_API_KEY=your_api_key_here
```

#### 客户端配置

在 MCP 客户端的配置文件中添加 SSE 服务器地址：

```json
{
  "mcpServers": {
    "web-mcp": {
      "url": "http://your-server-address:port/sse"
    }
  }
}
```

**注意**: 将 `http://your-server-address:port/sse` 替换为实际的服务器地址。

### 可用工具

web-mcp 提供以下两个工具：

#### 1. web_search

执行 Web 搜索并返回结果。

**注意**: 使用此工具前必须先配置 API Key。

| 参数            | 类型     | 必填 | 默认值  | 描述             |
|---------------|--------|----|------|----------------|
| `query`       | string | ✅  | -    | 搜索关键词          |
| `num_results` | int    | ❌  | `10` | 返回结果数量，范围 1-50 |

**环境变量配置**:

在项目根目录创建 `.env` 文件，并配置以下内容：

```env
# 百度智能云 AppBuilder API Key（必需）
# 获取方式：https://console.bce.baidu.com/qianfan/ais/console/apiKey
BAIDU_API_KEY=your_api_key_here
```

#### 2. web_reader

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

MCP 客户端会自动调用 `web_reader` 工具并返回网页内容。

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
      "date": "2024-01-15",
      "website": "example.com",
      "rerank_score": 0.95,
      "authority_score": 0.88,
      "rank": 1
    }
  ],
  "total_results": 10
}
```

#### web_reader 返回格式

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

