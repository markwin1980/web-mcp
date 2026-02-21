# WEB_SEARCH.md

## 核心功能

Web-Search 模块使用 Playwright 访问 Bing.com 进行网页搜索，返回真实的搜索结果。支持翻页获取更多结果，无需 API Key。

## 处理流程

```
接收请求 → 参数验证 → 获取浏览器服务 → 访问 Bing 首页 → 输入搜索词 → 提取结果 → 翻页（如需要） → 返回 JSON
```

## 组件说明

### BingClient (`bing_client.py`)

- 使用传入的浏览器服务进行搜索（由外部管理浏览器生命周期）
- 支持翻页获取更多结果
- 自动从 Bing 搜索结果页面提取 title、url、snippet

### BingSearchConfig (`config.py`)

| 配置项                  | 默认值                   | 说明           |
|----------------------|-----------------------|--------------|
| `base_url`           | "https://cn.bing.com" | Bing 首页 URL  |
| `timeout`            | `30000`               | 页面加载超时时间（毫秒） |
| `page_load_delay`    | `1.0`                 | 页面加载后等待时间（秒） |
| `result_parse_delay` | `0.5`                 | 结果解析后等待时间（秒） |
| `results_per_page`   | `10`                  | 每页结果数量       |
| `max_results`        | `50`                  | 允许的最大搜索结果数量  |

### 异常类 (`exceptions.py`)

| 异常                 | 触发场景        |
|--------------------|-------------|
| `BingSearchError`  | Bing 搜索错误基类 |
| `PageLoadError`    | 页面加载错误      |
| `ResultParseError` | 结果解析错误      |

## 搜索结果字段

每个搜索结果包含以下字段：

| 字段        | 类型     | 说明           |
|-----------|--------|--------------|
| `title`   | string | 网页标题         |
| `url`     | string | 网页地址         |
| `snippet` | string | 网页内容摘要       |
| `rank`    | int    | 结果排名（从 1 开始） |

## 日志记录

- 日志文件存储在 `log/` 目录
- 文件名格式：`web_search_YYYYMMDD.log`
- 记录所有请求和响应（成功/失败）

## 使用要求

1. **浏览器安装**：需要运行 `playwright install chromium` 安装浏览器

## 搜索流程详解

1. **获取浏览器服务**：从全局浏览器服务获取可用的浏览器页面
2. **访问 Bing 首页**：导航到 `https://cn.bing.com`
3. **输入搜索词**：在搜索框中输入关键词并按回车
4. **等待结果加载**：等待 `li.b_algo` 元素出现
5. **提取搜索结果**：解析每个结果的标题、URL 和摘要
6. **翻页（如需要）**：如果结果数量不足，点击"下一页"按钮继续搜索
7. **释放页面**：将页面释放回页面池
8. **返回结果**：返回请求数量的结果，带 rank 排名

## CSS 选择器

- **搜索结果容器**：`li.b_algo`
- **标题链接**：`h2 a`
- **摘要**：`p.b_algoSlug` 或 `div.b_caption p`
