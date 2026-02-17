# CLAUDE.md

## 内容输出要求

1. 使用中文输出所有回答
2. 项目目录结构在[STRUCT.md](docs/claude/STRUCT.md), 需要更新目录结构时, 请确保：
    - 同层级内：目录在前，文件在后
    - 同类型（目录或文件）：按字母顺序排列
    - 被[.gitignore](.gitignore)排除的文件和目录不显示

## 项目概述

MCP 服务器，MCP 服务器，提供Web搜索，Web读取等功能

## 技术栈

- **Python 版本**: 3.11+
- **依赖管理**: uv
- aiohttp >= 3.9.0（异步 HTTP 客户端）
- markdownify >= 0.13.1（HTML 转 Markdown）
- readabilipy >= 0.2.0（内容提取）
- beautifulsoup4 >= 4.12.0（HTML 解析）
- pydantic >= 2.0.0（数据验证）
- mcp >= 1.26.0（MCP 协议支持）

## 专项说明文档

只读取下面列出的文档，其他的markdown文档是给用户参考的，不要读取

| 说明文档                                       | 读取条件              |
|--------------------------------------------|-------------------|
| [STRUCT.md](docs/claude/STRUCT.md)         | 需要查询项目目录结构时       |
| [TEST.md](docs/claude/TEST.md)             | 需要对脚本进行运行测试时      |
| [MCP_SERVER.md](docs/claude/MCP_SERVER.md) | 处理mcp服务器相关问题时     |
| [WEB_READER.md](docs/claude/WEB_READER.md) | 处理web_reader相关问题时 |

