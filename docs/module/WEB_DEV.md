# WEB_DEV.md

## 核心功能

Web-Dev 模块提供网页开发调试工具，支持会话管理、网页操作、元素信息查询、Console 日志捕获和截图功能。通过单一综合工具`web_dev`
使用 `action` 参数区分不同操作。

## 处理流程

```
接收请求 → 验证 action 参数 → 会话管理 → 执行对应操作 → 返回 JSON 结果
```

## 组件说明

### web_dev (`web_dev.py`)

- 单一综合工具入口，通过 `action` 参数分发到具体操作
- 统一的 JSON 返回格式（success, action, session_id, data, error, timestamp）
- 完整的日志记录和错误处理

### SessionManager (`session_manager.py`)

- 全局单例模式，管理多个调试会话
- 使用 UUID 生成会话 ID
- 从 browser_service 获取和释放页面
- 使用 `asyncio.Lock` 保证并发安全

### DevSession (`dev_session.py`)

- 封装单个调试会话，持有 Playwright Page 对象
- 设置 console 和 pageerror 事件监听器
- 提供各类网页操作方法（导航、点击、输入、下拉、鼠标/键盘操作等）
- 提供查询方法（元素信息、页面信息、元素搜索）
- 提供截图功能（页面截图、元素截图）

### ConsoleHandler (`console_handler.py`)

- 捕获和管理 console 日志
- 监听 `page.on("console")` 和 `page.on("pageerror")` 事件
- 存储日志（时间戳、类型、消息、堆栈、位置）
- 支持按类型过滤和数量限制获取日志

### WebDevConfig (`config.py`)

配置类（预留扩展），目前无配置项。

### 异常类 (`exceptions.py`)

| 异常                     | 触发场景         |
|------------------------|--------------|
| `WebDevError`          | Web-Dev 错误基类 |
| `SessionNotFoundError` | 会话不存在错误      |
| `SessionCreationError` | 会话创建错误       |
| `InvalidActionError`   | 无效的操作类型错误    |
| `ElementNotFoundError` | 元素未找到错误      |
| `NavigationError`      | 导航错误         |
| `ScreenshotError`      | 截图错误         |
| `ActionExecutionError` | 操作执行错误       |

## 支持的 Action 列表

### 会话管理

| Action           | 必需参数       | 说明                  |
|------------------|------------|---------------------|
| `create_session` | -          | 创建新会话，返回 session_id |
| `close_session`  | session_id | 关闭指定会话              |
| `list_sessions`  | session_id | 列出所有活跃会话            |

### 导航操作

| Action       | 必需参数            | 可选参数                | 说明      |
|--------------|-----------------|---------------------|---------|
| `navigate`   | session_id, url | timeout, wait_until | 导航到 URL |
| `go_back`    | session_id      | -                   | 后退      |
| `go_forward` | session_id      | -                   | 前进      |
| `reload`     | session_id      | -                   | 刷新页面    |

### 元素操作

| Action          | 必需参数                                         | 可选参数                          | 说明       |
|-----------------|----------------------------------------------|-------------------------------|----------|
| `click`         | session_id, selector                         | timeout, force, no_wait_after | 点击元素     |
| `fill`          | session_id, selector, value                  | timeout                       | 填充输入框    |
| `type_text`     | session_id, selector, text                   | delay, timeout                | 逐个字符输入文本 |
| `clear`         | session_id, selector                         | timeout                       | 清空输入框    |
| `select_option` | session_id, selector                         | values, labels, timeout       | 选择下拉选项   |
| `check`         | session_id, selector                         | timeout                       | 勾选复选框    |
| `uncheck`       | session_id, selector                         | timeout                       | 取消勾选复选框  |
| `hover`         | session_id, selector                         | timeout                       | 鼠标悬停     |
| `drag_and_drop` | session_id, source_selector, target_selector | timeout                       | 拖放操作     |
| `focus`         | session_id, selector                         | timeout                       | 聚焦元素     |

### 键盘和鼠标操作

| Action      | 必需参数            | 可选参数  | 说明                  |
|-------------|-----------------|-------|---------------------|
| `press_key` | session_id, key | delay | 按下键盘按键              |
| `scroll`    | session_id      | x, y  | 滚动页面（至少需要 x 或 y 之一） |

### 查询操作

| Action             | 必需参数                 | 可选参数    | 说明           |
|--------------------|----------------------|---------|--------------|
| `get_element_info` | session_id, selector | timeout | 获取元素信息       |
| `get_page_info`    | session_id           | -       | 获取页面信息       |
| `search_elements`  | session_id, selector | timeout | 搜索元素（返回元素列表） |

### Console 日志

| Action               | 必需参数       | 可选参数        | 说明            |
|----------------------|------------|-------------|---------------|
| `get_console_logs`   | session_id | type, limit | 获取 console 日志 |
| `clear_console_logs` | session_id | -           | 清空 console 日志 |

### 截图

| Action       | 必需参数       | 可选参数                                         | 说明               |
|--------------|------------|----------------------------------------------|------------------|
| `screenshot` | session_id | full_page, selector, scale, quality, timeout | 截图（返回 base64 数据） |

### JavaScript 执行和等待

| Action                | 必需参数                   | 可选参数           | 说明                |
|-----------------------|------------------------|----------------|-------------------|
| `evaluate`            | session_id, expression | -              | 执行 JavaScript 表达式 |
| `wait_for_selector`   | session_id, selector   | timeout, state | 等待元素出现            |
| `wait_for_load_state` | session_id             | state, timeout | 等待页面加载状态          |

## 返回格式

统一的 JSON 返回格式：

```json
{
  "success": true/false,
  "action": "action_name",
  "session_id": "session-uuid",
  "timestamp": "2026-02-22T10:30:00.000000",
  "data": {
    ...
  },
  "error": "error message (if failed)"
}
```

## 日志记录

- 日志文件存储在 `log/` 目录
- 文件名格式：`web_dev_YYYYMMDD.log`
- 记录所有请求和响应（成功/失败）

## 使用示例

### 创建会话

```json
{
  "action": "create_session"
}
```

### 导航到 URL

```json
{
  "action": "navigate",
  "session_id": "uuid-here",
  "url": "https://example.com"
}
```

### 点击元素

```json
{
  "action": "click",
  "session_id": "uuid-here",
  "selector": "#submit-button"
}
```

### 获取 Console 日志

```json
{
  "action": "get_console_logs",
  "session_id": "uuid-here",
  "type": "error",
  "limit": 10
}
```

### 截图

```json
{
  "action": "screenshot",
  "session_id": "uuid-here",
  "full_page": true
}
```

## 元素信息字段

| 字段             | 类型       | 说明                    |
|----------------|----------|-----------------------|
| `tag_name`     | string   | 标签名                   |
| `id`           | string   | 元素 ID                 |
| `classes`      | string[] | class 列表              |
| `text`         | string   | 文本内容                  |
| `inner_html`   | string   | 内部 HTML               |
| `attributes`   | object   | 属性字典                  |
| `bounding_box` | object   | 边界框（x,y,width,height） |
| `css_style`    | object   | CSS 样式字典              |
| `visible`      | boolean  | 是否可见                  |
| `enabled`      | boolean  | 是否启用                  |

## 页面信息字段

| 字段              | 类型     | 说明         |
|-----------------|--------|------------|
| `url`           | string | 当前 URL     |
| `title`         | string | 页面标题       |
| `viewport_size` | object | 视口大小       |
| `user_agent`    | string | User Agent |
| `cookies`       | array  | Cookie 列表  |
