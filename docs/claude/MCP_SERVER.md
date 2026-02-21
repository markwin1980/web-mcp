# MCP_SERVER.md

## 概述

使用 FastMCP 框架实现的 MCP 服务器，通过 stdio 传输与客户端通信，提供 web_search 和 url_fetcher 两个工具。

## 项目结构

入口文件：

- `mcp_stdio.py` - 使用 stdio 传输（本地使用）

- 创建 FastMCP 实例
- 注册 lifespan 生命周期管理（初始化和关闭浏览器）
- 注册 web_search 工具（来自 web_search 模块）
- 注册 url_fetcher 工具（来自 url_fetcher 模块）
- 调用 mcp.run() 启动服务器（指定 transport 参数）

## 工作流程

### 服务器启动

```
mcp_stdio.py → 创建 FastMCP → 注册 lifespan → 注册工具 → mcp.run(transport="stdio") → 等待客户端连接
                                    ↓
                              lifespan 启动 → initialize_global_browser() → 浏览器就绪
```

### 服务器关闭

```
客户端断开 → lifespan 退出 → close_global_browser() → 关闭浏览器 → 服务器退出
```

### url_fetcher 调用流程

1. 接收参数 → 验证 → WebClient 使用 Playwright 获取网页（通过 browser_service）→ 注入 Readability.js 提取文章 → HTMLParser
   解析转换 → 返回 JSON

### web_search 调用流程

1. 接收参数 → 验证 → 获取浏览器服务 → 访问 Bing 首页 → 输入搜索词 → 提取结果 → 翻页（如需要） → 返回 JSON

## 关键文件

| 文件                           | 说明               |
|------------------------------|------------------|
| `mcp_stdio.py`               | 服务器入口（stdio 传输）  |
| `url_fetcher/url_fetcher.py` | URL-Fetcher 工具实现 |
| `web_search/web_search.py`   | Web-Search 工具实现  |
