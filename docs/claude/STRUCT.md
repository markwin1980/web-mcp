# STRUCT.md

本文件包含项目的**目录结构**和**文件说明**，更新本文档只需要更新这2个部分。

## 目录结构

```
web-mcp/
├── docs/                   # 项目文档
│   └── claude/            # AI 助手专项说明文档
│       ├── MCP_SERVER.md  # MCP 服务器说明
│       ├── STRUCT.md      # 项目目录结构（本文件）
│       ├── TEST.md        # 测试运行说明
│       └── WEB_READER.md  # Web-Reader 模块说明
├── tests/                 # 测试套件
│   ├── fixtures/          # 测试数据
│   │   └── sample.html   # HTML 测试样本
│   ├── __init__.py       # 测试包初始化
│   ├── conftest.py       # pytest 配置和 fixtures
│   ├── test_fetcher.py   # 网页获取单元测试
│   ├── test_mcp_server.py # MCP 服务器集成测试
│   ├── test_parser.py    # HTML 解析器单元测试
│   ├── test_web_reader.py # Web-Reader 工具集成测试
│   └── test_web_search.py # Web-Search 工具集成测试
├── web_reader/            # Web-Reader 功能模块
│   ├── __init__.py       # 模块导出
│   ├── config.py         # 配置管理
│   ├── exceptions.py     # 自定义异常
│   ├── fetcher.py        # HTTP 请求和缓存管理
│   ├── models.py         # Pydantic 数据模型
│   ├── parser.py         # HTML 解析和转换
│   └── web_reader.py     # Web-Reader 工具实现
├── web_search/            # Web-Search 功能模块
│   ├── __init__.py       # 模块导出
│   └── web_search.py     # Web-Search 工具实现
├── .gitignore             # Git 忽略文件配置
├── .python-version        # Python 版本锁定
├── CLAUDE.md              # AI 助手的项目实现文档
├── main.py                # MCP 服务器主入口
├── pyproject.toml         # 项目配置
└── README.md              # 用户文档
```

## 文件说明

### 主入口

| 文件        | 说明                    |
|-----------|-----------------------|
| `main.py` | MCP 服务器主入口，定义工具和启动服务器 |

### Web-Reader 模块 (`web_reader/`)

| 文件              | 说明                     |
|-----------------|------------------------|
| `__init__.py`   | 模块导出，提供公共 API          |
| `config.py`     | 服务器配置参数管理              |
| `exceptions.py` | 自定义异常类定义               |
| `fetcher.py`    | HTTP 请求处理和内存缓存管理       |
| `models.py`     | Pydantic 数据模型定义（输入/输出） |
| `parser.py`     | HTML 解析、内容提取和格式转换      |
| `web_reader.py` | Web-Reader MCP 工具实现    |

### Web-Search 模块 (`web_search/`)

| 文件              | 说明                  |
|-----------------|---------------------|
| `__init__.py`   | 模块导出，提供公共 API       |
| `web_search.py` | Web-Search MCP 工具实现 |

### 测试 (`tests/`)

| 文件                   | 说明                    |
|----------------------|-----------------------|
| `__init__.py`        | 测试包初始化                |
| `conftest.py`        | pytest 配置和共享 fixtures |
| `fixtures/`          | 测试数据目录                |
| `test_fetcher.py`    | 网页获取和缓存单元测试           |
| `test_mcp_server.py` | MCP 服务器元数据和协议集成测试     |
| `test_parser.py`     | HTML 解析和转换单元测试        |
| `test_web_reader.py` | Web-Reader 工具集成测试     |
| `test_web_search.py` | Web-Search 工具集成测试     |

### 测试数据 (`tests/fixtures/`)

| 文件            | 说明        |
|---------------|-----------|
| `sample.html` | HTML 测试样本 |

### 项目文档 (`docs/claude/`)

| 文件              | 说明              |
|-----------------|-----------------|
| `MCP_SERVER.md` | MCP 服务器说明       |
| `STRUCT.md`     | 项目目录结构（本文件）     |
| `TEST.md`       | 测试运行说明          |
| `WEB_READER.md` | Web-Reader 模块说明 |

### 配置文件

| 文件                | 说明              |
|-------------------|-----------------|
| `.gitignore`      | Git 忽略文件配置      |
| `.python-version` | Python 版本锁定文件   |
| `pyproject.toml`  | 项目元数据、依赖配置和工具设置 |
| `README.md`       | 用户文档，介绍安装和使用方法  |
| `CLAUDE.md`       | AI 助手的项目实现文档    |
