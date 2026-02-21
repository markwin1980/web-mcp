# BROWSER_SERVICE.md

## 概述

基于 Playwright 的浏览器管理服务，提供浏览器实例的生命周期管理和页面池功能。支持页面复用以提高性能，集成
playwright-stealth-plugin
绕过反爬检测。

## 核心组件

| 类                | 文件                 | 说明                |
|------------------|--------------------|-------------------|
| `BrowserService` | browser_service.py | 浏览器服务主类，管理浏览器生命周期 |
| `PagePool`       | browser_service.py | 页面池管理器，复用页面       |
| `PooledPage`     | browser_service.py | 池化的页面对象           |
| `BrowserConfig`  | config.py          | 浏览器配置类            |

## 工作流程

### 初始化流程

```
MCP 服务器启动 → initialize_global_browser() → BrowserService.initialize() → 启动浏览器 → 创建页面池 → 就绪
```

### 页面获取流程

```
create_page() → PagePool.acquire() → 查找空闲页面 → (有) 返回页面 / (无) 创建新页面 → 返回
```

### 页面释放流程

```
release_page() → 标记页面为空闲 → 更新使用时间 → 检查是否超出限制 → 清理旧页面（如需要）
```

## 关键特性

### 页面池复用

- 优先复用池中的空闲页面
- 超过 `max_cached_pages` 时自动清理最旧的未使用页面
- 减少浏览器上下文创建开销

### 全局单例

- `get_global_browser_service()` - 获取全局浏览器服务实例
- `initialize_global_browser()` - 初始化全局浏览器
- `close_global_browser()` - 关闭全局浏览器

### 线程安全

- 使用 `asyncio.Lock` 保护页面池操作
- 避免竞态条件

## 配置

| 配置项                  | 默认值    | 说明       |
|----------------------|--------|----------|
| `headless`           | `True` | 是否无头模式   |
| `max_cached_pages`   | `10`   | 最大缓存页面数量 |
| `initial_page_count` | `1`    | 初始页面数量   |

**注意**：浏览器固定使用 Chromium，不支持配置其他浏览器类型。

### 环境变量

支持通过 `.env` 文件或环境变量配置浏览器行为：

| 环境变量               | 默认值    | 说明                                          |
|--------------------|--------|---------------------------------------------|
| `BROWSER_HEADLESS` | `true` | 是否使用无头模式                                    |
|                    |        | - `"1"`, `"true"`, `"yes"`, `"on"` → 启用无头模式 |
|                    |        | - 其他任何值 → 关闭无头模式（显示浏览器窗口，用于调试）              |

**示例 `.env` 文件**：

```env
# 启用无头模式（默认）
BROWSER_HEADLESS=true

# 关闭无头模式，显示浏览器窗口（调试用）
# BROWSER_HEADLESS=false
```

## 异常处理

| 异常类                          | 触发场景      |
|------------------------------|-----------|
| `BrowserInitializationError` | 浏览器初始化失败  |
| `PageCreationError`          | 创建页面失败    |
| `PageClosedError`            | 页面已关闭     |
| `BrowserError`               | 其他浏览器相关错误 |
