# BROWSER_SERVICE.md

## 概述

基于 Playwright 的浏览器管理服务，提供浏览器实例的生命周期管理和页面池功能。支持页面复用以提高性能，集成 stealth 脚本
绕过反爬检测。

## 核心组件

| 类                | 文件                 | 说明                       |
|------------------|--------------------|--------------------------|
| `BrowserService` | browser_service.py | 浏览器服务主类，管理浏览器生命周期        |
| `PagePool`       | browser_service.py | 页面池管理器，复用页面，维护单一 context |
| `PooledPage`     | browser_service.py | 池化的页面对象                  |
| `BrowserConfig`  | config.py          | 浏览器配置类                   |

## 工作流程

### 初始化流程

```
MCP 服务器启动 → initialize_global_browser() → BrowserService.initialize()
  ↓
加载 stealth 脚本 → 启动 Playwright → 启动 Chrome 浏览器 → 创建 browser context
  ↓
应用 stealth 脚本到 context → 创建页面池 → 预创建初始页面 → 就绪
```

### 页面获取流程

```
create_page() → PagePool.acquire() → 查找空闲页面 → (有) 返回页面 / (无) 创建新页面 → 返回
```

**重要**：所有页面在同一个 browser context 中创建，`new_context()` 只在初始化时执行一次。

### 页面释放流程

```
release_page() → 标记页面为空闲 → 更新使用时间 → 检查是否超出限制 → 清理旧页面（如需要）
```

**注意**：页面关闭时不会关闭 context，context 在 `close()` 时统一关闭。

### 关闭流程

```
close() → 关闭所有页面池页面 → 关闭 browser context → 关闭 browser → 停止 Playwright → 清空资源
```

## 关键特性

### Context 共享机制

- **单一 Context**：`new_context()` 只在初始化时执行一次
- **多页面共享**：所有页面在同一个 context 中创建，共享存储和 cookie
- **性能优势**：避免重复创建 context 的开销，页面创建速度更快
- **资源节约**：减少内存和系统资源占用

### 页面池复用

- 优先复用池中的空闲页面
- 超过 `max_cached_pages` 时自动清理最旧的未使用页面
- 减少页面创建开销

### Stealth 反检测

- **脚本加载**：初始化时从 `browser_service/stealth/stealth.js` 加载脚本
- **应用时机**：在 browser context 创建后立即应用
- **作用范围**：对 context 下所有页面生效
- **静默失败**：脚本加载失败不会影响浏览器正常启动

### 浏览器启动参数

浏览器使用以下参数启动以降低检测风险：

| 参数                                              | 说明                       |
|-------------------------------------------------|--------------------------|
| `--no-sandbox`                                  | 禁用沙箱模式                   |
| `--disable-setuid-sandbox`                      | 禁用 setuid 沙箱             |
| `--disable-blink-features=AutomationControlled` | 禁用自动化控制特征                |
| `--disable-infobars`                            | 禁用信息栏                    |
| `channel="chrome"`                              | 使用 Chrome 浏览器而非 Chromium |

### Context 配置

初始化时创建的 browser context 使用以下配置：

| 配置项                   | 值                                                                                                               | 说明                 |
|-----------------------|-----------------------------------------------------------------------------------------------------------------|--------------------|
| `user_agent`          | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 | 模拟真实浏览器 User-Agent |
| `viewport`            | 1280x720                                                                                                        | 桌面视口大小             |
| `device_scale_factor` | 1                                                                                                               | 设备缩放因子             |
| `is_mobile`           | False                                                                                                           | 非移动设备              |
| `has_touch`           | False                                                                                                           | 不支持触摸              |

### 全局单例

- `get_global_browser_service()` - 获取全局浏览器服务实例（线程安全）
- `initialize_global_browser()` - 初始化全局浏览器
- `close_global_browser()` - 关闭全局浏览器

### 线程安全

- 使用 `asyncio.Lock` 保护页面池操作
- 全局实例访问使用独立锁保护
- 避免竞态条件
- 确保共享 context 的并发访问安全

## 配置

| 配置项                  | 默认值    | 最大值   | 说明       |
|----------------------|--------|-------|----------|
| `headless`           | `True` | -     | 是否无头模式   |
| `max_cached_pages`   | `10`   | `100` | 最大缓存页面数量 |
| `initial_page_count` | `1`    | `10`  | 初始页面数量   |

**注意**：浏览器固定使用 Chrome，不支持配置其他浏览器类型。

### 环境变量

支持通过 `.env` 文件或环境变量配置浏览器行为：

| 环境变量                         | 默认值    | 最大值   | 说明                                          |
|------------------------------|--------|-------|---------------------------------------------|
| `BROWSER_HEADLESS`           | `true` | -     | 是否使用无头模式                                    |
|                              |        |       | - `"1"`, `"true"`, `"yes"`, `"on"` → 启用无头模式 |
|                              |        |       | - 其他任何值 → 关闭无头模式（显示浏览器窗口，用于调试）              |
| `BROWSER_MAX_CACHED_PAGES`   | `10`   | `100` | 最大缓存页面数量，超过 100 会被自动限制为 100                 |
| `BROWSER_INITIAL_PAGE_COUNT` | `1`    | `10`  | 初始页面数量，超过 10 会被自动限制为 10                     |

**示例 `.env` 文件**：

```env
# 启用无头模式（默认）
BROWSER_HEADLESS=true

# 关闭无头模式，显示浏览器窗口（调试用）
# BROWSER_HEADLESS=false

# 设置最大缓存页面数为 50
BROWSER_MAX_CACHED_PAGES=50

# 设置初始页面数量为 3
BROWSER_INITIAL_PAGE_COUNT=3
```

## 异常处理

| 异常类                          | 触发场景      |
|------------------------------|-----------|
| `BrowserInitializationError` | 浏览器初始化失败  |
| `PageCreationError`          | 创建页面失败    |
| `PageClosedError`            | 页面已关闭     |
| `BrowserError`               | 其他浏览器相关错误 |
