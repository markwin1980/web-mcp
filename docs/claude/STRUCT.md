# STRUCT.md

本文件包含项目的**目录结构**。

## 内容输出要求

需要更新目录结构时, 请确保：

- 同层级内：目录在前，文件在后
- 同类型（目录或文件）：按字母顺序排列
- 被[.gitignore](/.gitignore)排除的文件和目录不显示

## 目录结构

```
web-mcp/
├── browser_service/       # 浏览器服务模块
│   ├── __init__.py       # 模块导出，提供公共 API
│   ├── browser_service.py # 浏览器和页面池管理（BrowserService）
│   ├── config.py         # BrowserConfig 浏览器配置类（支持环境变量）
│   └── exceptions.py     # 浏览器相关异常类定义
├── docs/                  # 项目文档
│   ├── claude/           # AI 助手专项说明文档
│   │   ├── GIT.md        # Git 提交规范
│   │   ├── STRUCT.md     # 项目目录结构（本文件）
│   │   └── TEST.md       # 测试运行说明
│   └── module/           # 模块详细说明文档
│       ├── BROWSER_SERVICE.md # 浏览器服务模块说明
│       ├── MCP_SERVER.md # MCP 服务器说明
│       ├── URL_FETCHER.md # URL-Fetcher 模块说明
│       └── WEB_SEARCH.md # Web-Search 模块说明
├── res/                   # 资源文件
│   └── Readability.js    # Mozilla Readability.js 脚本
├── tests/                # 测试套件
│   ├── __init__.py      # 测试包初始化
│   ├── conftest.py      # pytest 配置和共享 fixtures
│   ├── test_browser_service.py # 浏览器服务单元测试
│   ├── test_mcp_server.py # MCP 服务器元数据和协议集成测试
│   ├── test_url_fetcher.py # URL-Fetcher 工具集成测试
│   └── test_web_search.py   # Web-Search 工具集成测试
├── url_fetcher/           # URL-Fetcher 功能模块
│   ├── __init__.py      # 模块导出，提供公共 API
│   ├── config.py        # FetcherConfig 配置类
│   ├── exceptions.py    # 自定义异常类定义
│   ├── html_parser.py   # HTML 解析、内容提取和格式转换
│   ├── url_fetcher.py   # URL-Fetcher MCP 工具实现
│   └── web_client.py    # Playwright 网页获取客户端
├── web_search/           # Web-Search 功能模块
│   ├── __init__.py      # 模块导出，提供公共 API
│   ├── bing_client.py   # Bing 搜索客户端（使用 Playwright）
│   ├── config.py        # BingSearchConfig 搜索配置类
│   ├── exceptions.py    # 自定义异常类定义
│   └── web_search.py    # Web-Search MCP 工具实现
├── .gitignore            # Git 忽略文件配置
├── .python-version       # Python 版本锁定文件
├── CLAUDE.md             # AI 助手的项目实现文档
├── mcp_stdio.py          # MCP 服务器入口（stdio 传输，本地使用）
├── pyproject.toml        # 项目元数据、依赖配置和工具设置
└── README.md             # 用户文档，介绍安装和使用方法
```
