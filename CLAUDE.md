# CLAUDE.md

## 内容输出要求

使用中文输出所有回答

## 项目概述

MCP 服务器，提供Web搜索，URL获取等功能

**核心架构**：`browser_service`（浏览器池）→ `url_fetcher`/`web_search`（功能模块）→ `mcp_stdio.py`（MCP入口）

## 开发说明

### 行为约束

**禁止主动执行以下操作，除非得到用户明确指令**

- **Git 提交** - 不自动提交代码
- **测试运行** - 不自动运行测试
- **服务启动** - 不主动启动本地测试服务
- **推送远程** - 提交后不自动推送到远程仓库
- **依赖安装** - 不自动安装依赖
- **文件创建** - 不创建不必要的文件（临时文档、临时测试代码文件、配置文件、日志等）

### 开发要求

- **文档同步** - 修改代码后同步更新相关文档
- **最小化改动** - 修改功能时只改相关文件，涉及其他文件需先询问用户
- **避免过度设计** - 只做用户要求的事，不添加未被要求的功能或"改进"
- **询问确认** - 有多种实现方式时，先询问用户偏好

## 文档说明

如需获取具体项目信息，或对项目文件进行了增删改等操作，参照下表来读取/修改文档。

| 说明文档                                                 | 读取条件                   | 修改条件（影响的文件）                   |
|------------------------------------------------------|------------------------|-------------------------------|
| [STRUCT.md](docs/claude/STRUCT.md)                   | 需要查询项目目录结构时            | 所有新增/删除的文件或目录结构变化             |
| [TEST.md](docs/claude/TEST.md)                       | 需要对脚本进行运行测试时           | `tests/` 下所有文件                |
| [GIT.md](docs/claude/GIT.md)                         | 需要查看 Git 提交规范时         | 无（规范变更除外）                     |
| [MCP_SERVER.md](docs/module/MCP_SERVER.md)           | 处理mcp服务器相关问题时          | `mcp_stdio.py`, `mcp_http.py` |
| [BROWSER_SERVICE.md](docs/module/BROWSER_SERVICE.md) | 处理browser_service相关问题时 | `browser_service/` 下所有文件      |
| [URL_FETCHER.md](docs/module/URL_FETCHER.md)         | 处理url_fetcher相关问题时     | `url_fetcher/` 下所有文件          |
| [WEB_SEARCH.md](docs/module/WEB_SEARCH.md)           | 处理web_search相关问题时      | `web_search/` 下所有文件           |
| [README.md](README.md)                               | 无（用户文档，无需读取）           | 功能增减、API 变更、配置方式变化            |
| [.env.example](.env.example)                         | 无（范例文件，无需读取）           | 环境变量新增/删除/默认值变更               |
