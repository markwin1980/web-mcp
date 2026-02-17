# MCP_SERVER.md

## 概述

使用 FastMCP 框架实现的 MCP 服务器，通过 stdio 传输与客户端通信，提供 web_search 和 web_reader 两个工具。

## 项目结构

入口文件：

- `mcp_stdio.py` - 使用 stdio 传输（本地使用）
- `mcp_sse.py` - 使用 SSE 传输（服务器部署）

- 创建 FastMCP 实例
- 注册 web_search 工具（来自 web_search 模块）
- 注册 web_reader 工具（来自 web_reader 模块）
- 调用 mcp.run() 启动服务器（指定 transport 参数）

## 工作流程

### 服务器启动

```
mcp_stdio.py / mcp_sse.py → 创建 FastMCP → 注册工具 → mcp.run(transport="...") → 等待客户端连接
```

### web_reader 调用流程

1. 接收参数 → 验证 → WebFetcher 获取 HTML（带缓存）→ HTMLParser 解析转换 → 返回 JSON

### web_search 调用流程

1. 接收参数 → 验证 → BaiduSearchClient 调用百度千帆 API → 解析结果 → 返回 JSON

## 关键文件

| 文件                         | 说明              |
|----------------------------|-----------------|
| `mcp_stdio.py`             | 服务器入口（stdio 传输） |
| `mcp_sse.py`               | 服务器入口（SSE 传输）   |
| `web_reader/web_reader.py` | Web 读取工具实现      |
| `web_search/web_search.py` | Web 搜索工具实现      |
