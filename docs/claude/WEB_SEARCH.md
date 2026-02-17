# WEB_SEARCH.md

## 核心功能

Web-Search 模块使用百度智能云千帆 AI 搜索 API 进行网页搜索，返回高质量的搜索结果。

## 处理流程

```
接收请求 → 参数验证 → BaiduSearchClient 调用千帆 API → 解析结果 → 返回 JSON
```

## 组件说明

### BaiduSearchClient (`client.py`)

- 使用 aiohttp 进行异步 HTTP 请求
- 实现重试机制（默认 3 次）
- 支持指数退避重试策略
- 处理 429 请求限流
- 解析 API 响应并提取网页结果
-

### 配置 (`config.py`)

| 配置项             | 默认值                                                    | 说明                       |
|-----------------|--------------------------------------------------------|--------------------------|
| `api_key`       | 从环境变量 `BAIDU_API_KEY` 读取                               | 百度智能云 AppBuilder API Key |
| `base_url`      | "https://qianfan.baidubce.com/v2/ai_search/web_search" | 千帆 AI 搜索 API 基础 URL      |
| `timeout`       | 30                                                     | 请求超时时间（秒）                |
| `max_retries`   | 3                                                      | 最大重试次数                   |
| `search_source` | "baidu_search_v2"                                      | 搜索引擎版本，固定值               |

### 异常类 (`exceptions.py`)

| 异常                     | 触发场景             |
|------------------------|------------------|
| `BaiduSearchError`     | 百度搜索错误基类         |
| `BaiduSearchAuthError` | 认证错误（API Key 无效） |
| `BaiduSearchAPIError`  | API 返回错误         |

## 搜索结果字段

每个搜索结果包含以下字段：

| 字段                | 类型     | 说明                |
|-------------------|--------|-------------------|
| `title`           | string | 网页标题              |
| `url`             | string | 网页地址              |
| `snippet`         | string | 网页内容摘要（最多 2000 字） |
| `date`            | string | 网页日期              |
| `website`         | string | 站点名称              |
| `rerank_score`    | float  | 相关性评分（0-1，越大越相关）  |
| `authority_score` | float  | 权威性评分（0-1，越大越权威）  |
| `rank`            | int    | 结果排名（从 1 开始）      |

## 日志记录

- 日志文件存储在 `log/` 目录
- 文件名格式：`web_search_YYYYMMDD.log`
- 记录所有请求和响应（成功/失败）
