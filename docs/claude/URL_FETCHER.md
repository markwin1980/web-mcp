# URL_FETCHER.md

## 核心功能

URL-Fetcher 模块负责读取网页内容，使用 Playwright + Readability.js 提取主要文本并转换为 Markdown 或纯文本格式。

## 处理流程

```
接收请求 → URL 验证 → WebClient 获取 HTML（使用 Playwright） → HTMLParser 解析 → 返回 JSON
```

## 组件说明

### WebClient (`web_client.py`)

- 使用 Playwright 浏览器加载网页
- 注入并运行 Mozilla Readability.js 提取文章内容
- 验证 URL 协议（必须是 http:// 或 https://）
- 使用 browser_service 管理页面生命周期
- Readability.js 脚本位置：`res/Readability.js`

### HTMLParser (`html_parser.py`)

- 解析 Readability.js 的输出
- 使用 BeautifulSoup 解析 HTML
- 使用 markdownify 转换为 Markdown
- 提取标题、摘要、内容和元数据
- 支持保留/移除图片

### 配置 (`config.py`)

| 配置项               | 默认值 | 说明      |
|-------------------|-----|---------|
| `default_timeout` | 20  | 默认超时（秒） |

### 异常类 (`exceptions.py`)

| 异常                   | 触发场景      |
|----------------------|-----------|
| `URLValidationError` | URL 格式无效  |
| `FetchError`         | HTTP 请求失败 |
| `ParseError`         | HTML 解析失败 |

## 元数据提取

从 Readability.js 输出中提取的元数据包括：

- `author`: 作者
- `word_count`: 字数统计
- `site_name`: 网站名称

## 日志记录

- 日志文件存储在 `log/` 目录
- 文件名格式：`url_fetcher_YYYYMMDD.log`
- 记录所有请求和响应（成功/失败）
