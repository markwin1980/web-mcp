# URL_FETCHER.md

## 核心功能

URL-Fetcher 模块负责读取网页内容，提取主要文本并转换为 Markdown 或纯文本格式。

## 处理流程

```
接收请求 → URL 验证 → WebFetcher 获取 HTML（带缓存）→ HTMLParser 解析 → 返回 JSON
```

## 组件说明

### WebFetcher (`fetcher.py`)

- 使用 aiohttp 进行异步 HTTP 请求
- 实现内存缓存机制，避免重复请求
- 支持 `no_cache` 参数绕过缓存
- 验证 URL 协议（必须是 http:// 或 https://）
- 检查内容大小限制（默认 1MB）

### HTMLParser (`parser.py`)

- 使用 readabilipy 提取网页主要内容
- 使用 BeautifulSoup 解析 HTML
- 使用 markdownify 转换为 Markdown
- 提取标题、摘要、内容和元数据
- 支持保留/移除图片

### 数据模型 (`models.py`)

**URLFetcherInput** - 输入参数：

- `url`: 目标网址
- `return_format`: 输出格式（markdown/text）
- `retain_images`: 是否保留图片
- `timeout`: 请求超时（5-60秒）
- `no_cache`: 是否绕过缓存

**ParseResult** - 解析结果：

- `url`: 原始网址
- `title`: 网页标题
- `summary`: 摘要（最多 200 字符）
- `content`: 转换后的内容
- `metadata`: 元数据字典
- `success`: 是否成功

### 配置 (`config.py`)

| 配置项                  | 默认值               | 说明              |
|----------------------|-------------------|-----------------|
| `user_agent`         | "URL-Fetcher/1.0" | HTTP User-Agent |
| `max_content_length` | 1,000,000         | 最大内容字节数         |
| `cache_ttl`          | 3600              | 缓存有效期（秒）        |
| `default_timeout`    | 20                | 默认超时（秒）         |

### 异常类 (`exceptions.py`)

| 异常                   | 触发场景      |
|----------------------|-----------|
| `URLValidationError` | URL 格式无效  |
| `FetchError`         | HTTP 请求失败 |
| `ParseError`         | HTML 解析失败 |

## 缓存机制

- 存储在内存字典 `_cache` 中，key 为 URL
- value 为 `(html_content, timestamp)` 元组
- 过期时间由 `cache_ttl` 配置（默认 1 小时）
- 可通过 `no_cache=True` 绕过缓存
- 提供 `clear_cache()` 方法清空缓存

## 元数据提取

从 HTML 中提取的元数据包括：

- `author`: 作者
- `publish_date`: 发布日期
- `word_count`: 字数统计
- `image_count`: 图片数量
- `og_title`: Open Graph 标题
- `og_description`: Open Graph 描述
- `og_image`: Open Graph 图片
- `site_name`: 网站名称

## 日志记录

- 日志文件存储在 `log/` 目录
- 文件名格式：`url_fetcher_YYYYMMDD.log`
- 记录所有请求和响应（成功/失败）
