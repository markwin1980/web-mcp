"""浏览器服务模块的单元测试。"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from playwright.async_api import Browser, BrowserContext, Page

from browser_service import (
    BrowserConfig,
    BrowserError,
    BrowserInitializationError,
    BrowserService,
    PageClosedError,
    PageCreationError,
    close_global_browser,
    get_global_browser_service,
    initialize_global_browser,
)
from browser_service.browser_service import PagePool, PooledPage


# ============================================================================
# PooledPage 测试
# ============================================================================


@pytest.mark.asyncio
async def test_pooled_page_creation():
    """测试 PooledPage 创建。"""
    mock_page = MagicMock(spec=Page)
    mock_context = MagicMock(spec=BrowserContext)

    pooled = PooledPage(
        page=mock_page,
        context=mock_context,
        in_use=False,
        last_used=0.0,
    )

    assert pooled.page == mock_page
    assert pooled.context == mock_context
    assert pooled.in_use is False
    assert pooled.last_used == 0.0


# ============================================================================
# PagePool 测试
# ============================================================================


@pytest.fixture
def mock_browser():
    """创建模拟浏览器。"""
    browser = MagicMock(spec=Browser)
    browser.new_context = AsyncMock()
    return browser


@pytest.fixture
def mock_stealth():
    """创建模拟 Stealth 实例。"""
    stealth = MagicMock()
    stealth.apply_stealth_async = AsyncMock()
    return stealth


@pytest.fixture
def browser_config():
    """创建浏览器配置。"""
    return BrowserConfig(
        max_cached_pages=3,
        initial_page_count=1,
    )


@pytest.fixture
async def page_pool(mock_browser, mock_stealth, browser_config):
    """创建 PagePool 实例。"""
    return PagePool(
        browser=mock_browser,
        stealth=mock_stealth,
        config=browser_config,
    )


@pytest.mark.asyncio
async def test_page_pool_initialize(page_pool, mock_browser, mock_stealth, browser_config):
    """测试页面池初始化。"""
    # 创建模拟的页面对象
    mock_context = MagicMock(spec=BrowserContext)
    mock_page = MagicMock(spec=Page)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser.new_context = AsyncMock(return_value=mock_context)

    # 初始化页面池
    await page_pool.initialize()

    # 验证创建了一个页面
    assert len(page_pool._pool) == 1
    assert mock_browser.new_context.call_count == 1
    assert mock_context.new_page.call_count == 1
    assert mock_stealth.apply_stealth_async.call_count == 1

    # 验证页面状态
    pooled = page_pool._pool[0]
    assert pooled.page == mock_page
    assert pooled.context == mock_context
    assert pooled.in_use is False


@pytest.mark.asyncio
async def test_page_pool_acquire_reuse(page_pool, mock_browser, mock_stealth):
    """测试从页面池复用页面。"""
    # 创建模拟的页面对象
    mock_context = MagicMock(spec=BrowserContext)
    mock_page = MagicMock(spec=Page)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser.new_context = AsyncMock(return_value=mock_context)

    # 初始化页面池
    await page_pool.initialize()

    # 获取页面（应该复用）
    acquired_page = await page_pool.acquire()

    # 验证复用了池中的页面
    assert acquired_page == mock_page
    assert page_pool._pool[0].in_use is True

    # 验证没有创建新页面
    assert mock_browser.new_context.call_count == 1


@pytest.mark.asyncio
async def test_page_pool_acquire_new(page_pool, mock_browser, mock_stealth):
    """测试创建新页面当池中无空闲页面时。"""
    # 创建模拟的页面对象
    mock_context1 = MagicMock(spec=BrowserContext)
    mock_page1 = MagicMock(spec=Page)
    mock_context1.new_page = AsyncMock(return_value=mock_page1)

    mock_context2 = MagicMock(spec=BrowserContext)
    mock_page2 = MagicMock(spec=Page)
    mock_context2.new_page = AsyncMock(return_value=mock_page2)

    mock_browser.new_context = AsyncMock(side_effect=[mock_context1, mock_context2])

    # 初始化页面池（创建一个页面）
    await page_pool.initialize()

    # 标记第一个页面为使用中
    page_pool._pool[0].in_use = True

    # 获取页面（应该创建新的）
    acquired_page = await page_pool.acquire()

    # 验证创建了新页面
    assert acquired_page == mock_page2
    assert len(page_pool._pool) == 2
    assert mock_browser.new_context.call_count == 2


@pytest.mark.asyncio
async def test_page_pool_release(page_pool, mock_browser):
    """测试释放页面。"""
    # 创建模拟的页面对象
    mock_context = MagicMock(spec=BrowserContext)
    mock_page = MagicMock(spec=Page)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser.new_context = AsyncMock(return_value=mock_context)

    # 初始化页面池
    await page_pool.initialize()

    # 获取并标记为使用中
    page = await page_pool.acquire()
    assert page_pool._pool[0].in_use is True

    # 释放页面
    await page_pool.release(page)

    # 验证页面被标记为未使用
    assert page_pool._pool[0].in_use is False


@pytest.mark.asyncio
async def test_page_pool_cleanup(page_pool, mock_browser):
    """测试页面池不会清理不超过限制的页面。"""
    # 创建多个模拟的页面对象
    contexts = []
    pages = []

    for i in range(5):
        mock_context = MagicMock(spec=BrowserContext)
        mock_page = MagicMock(spec=Page)
        mock_page.close = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        contexts.append(mock_context)
        pages.append(mock_page)

    mock_browser.new_context = AsyncMock(side_effect=contexts)

    # 初始化并创建多个页面
    await page_pool.initialize()  # 创建1个（索引0）
    # 获取3次：第1次复用索引0，第2次创建索引1，第3次创建索引2
    for _ in range(3):
        await page_pool.acquire()

    # 现在有3个页面（索引0-2），标记部分为未使用
    page_pool._pool[0].in_use = False
    page_pool._pool[0].last_used = 1.0
    page_pool._pool[1].in_use = True  # 使用中
    page_pool._pool[1].last_used = 2.0
    page_pool._pool[2].in_use = False
    page_pool._pool[2].last_used = 3.0

    # 释放一个页面，不会触发清理（max_cached_pages=3，当前3个）
    await page_pool.release(page_pool._pool[1].page)

    # 应该没有页面被关闭
    assert len(page_pool._pool) == 3


@pytest.mark.asyncio
async def test_page_pool_cleanup_when_exceeded(page_pool, mock_browser):
    """测试页面池清理超过限制的页面。"""
    # 创建多个模拟的页面对象
    contexts = []
    pages = []

    for i in range(5):
        mock_context = MagicMock(spec=BrowserContext)
        mock_page = MagicMock(spec=Page)
        mock_page.close = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        contexts.append(mock_context)
        pages.append(mock_page)

    mock_browser.new_context = AsyncMock(side_effect=contexts)

    # 初始化并创建多个页面
    await page_pool.initialize()  # 创建1个（索引0）
    # 获取4次：第1次复用索引0，第2、3、4次创建索引1、2、3
    for _ in range(4):
        await page_pool.acquire()

    # 现在有4个页面（索引0-3，max_cached_pages=3），标记部分为未使用
    page_pool._pool[0].in_use = False
    page_pool._pool[0].last_used = 1.0
    page_pool._pool[1].in_use = True  # 使用中
    page_pool._pool[1].last_used = 2.0
    page_pool._pool[2].in_use = False
    page_pool._pool[2].last_used = 3.0
    page_pool._pool[3].in_use = False
    page_pool._pool[3].last_used = 4.0

    # 释放一个页面，触发清理（max_cached_pages=3，当前4个，需关闭1个）
    await page_pool.release(page_pool._pool[1].page)

    # 应该关闭1个最旧的未使用页面（索引0）
    assert len(page_pool._pool) == 3  # 清理后剩余3个


@pytest.mark.asyncio
async def test_page_pool_close_all(page_pool, mock_browser):
    """测试关闭所有页面。"""
    # 创建模拟的页面对象
    mock_context = MagicMock(spec=BrowserContext)
    mock_page = MagicMock(spec=Page)
    mock_page.close = AsyncMock()
    mock_context.close = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser.new_context = AsyncMock(return_value=mock_context)

    # 初始化页面池
    await page_pool.initialize()

    # 关闭所有页面
    await page_pool.close_all()

    # 验证所有页面被关闭
    mock_page.close.assert_called_once()
    mock_context.close.assert_called_once()
    assert len(page_pool._pool) == 0


# ============================================================================
# BrowserService 测试
# ============================================================================


@pytest.fixture
def browser_service():
    """创建 BrowserService 实例。"""
    config = BrowserConfig(headless=True)
    return BrowserService(config)


@pytest.mark.asyncio
async def test_browser_service_not_initialized(browser_service):
    """测试未初始化状态。"""
    assert browser_service.is_initialized is False


@pytest.mark.asyncio
async def test_browser_service_initialize_chromium(browser_service):
    """测试初始化 Chromium 浏览器。"""
    with patch("playwright.async_api.async_playwright") as mock_playwright_fn:
        # 设置模拟
        mock_playwright = MagicMock()
        mock_playwright.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock()
        mock_browser = MagicMock(spec=Browser)
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_playwright_fn.return_value = mock_playwright

        # 初始化
        await browser_service.initialize()

        # 验证
        assert browser_service.is_initialized is True
        mock_playwright.chromium.launch.assert_called_once_with(headless=True)


@pytest.mark.asyncio
async def test_browser_service_initialize_firefox():
    """测试初始化 Firefox 浏览器。"""
    config = BrowserConfig(browser_type="firefox", headless=True)
    service = BrowserService(config)

    with patch("playwright.async_api.async_playwright") as mock_playwright_fn:
        # 设置模拟
        mock_playwright = MagicMock()
        mock_playwright.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.firefox.launch = AsyncMock()
        mock_browser = MagicMock(spec=Browser)
        mock_playwright.firefox.launch.return_value = mock_browser
        mock_playwright_fn.return_value = mock_playwright

        # 初始化
        await service.initialize()

        # 验证
        assert service.is_initialized is True
        mock_playwright.firefox.launch.assert_called_once_with(headless=True)


@pytest.mark.asyncio
async def test_browser_service_initialize_unsupported_browser():
    """测试初始化不支持的浏览器类型。"""
    config = BrowserConfig(browser_type="unsupported")
    service = BrowserService(config)

    with patch("playwright.async_api.async_playwright") as mock_playwright_fn:
        mock_playwright = MagicMock()
        mock_playwright.start = AsyncMock(return_value=mock_playwright)
        mock_playwright_fn.return_value = mock_playwright

        # 应该抛出异常
        with pytest.raises(BrowserInitializationError, match="不支持的浏览器类型"):
            await service.initialize()


@pytest.mark.asyncio
async def test_browser_service_create_page_without_init(browser_service):
    """测试未初始化时创建页面。"""
    with pytest.raises(BrowserError, match="浏览器未初始化"):
        await browser_service.create_page()


@pytest.mark.asyncio
async def test_browser_service_create_page(browser_service):
    """测试创建页面。"""
    # 模拟浏览器和页面
    mock_browser = MagicMock(spec=Browser)
    mock_context = MagicMock(spec=BrowserContext)
    mock_page = MagicMock(spec=Page)

    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser.new_context = AsyncMock(return_value=mock_context)

    with patch("playwright.async_api.async_playwright") as mock_playwright_fn:
        mock_playwright = MagicMock()
        mock_playwright.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright_fn.return_value = mock_playwright

        # 初始化
        await browser_service.initialize()

        # 创建页面
        page = await browser_service.create_page()

        # 验证
        assert page == mock_page


@pytest.mark.asyncio
async def test_browser_service_close(browser_service):
    """测试关闭浏览器服务。"""
    # 模拟浏览器
    mock_browser = MagicMock(spec=Browser)
    mock_browser.close = AsyncMock()

    with patch("playwright.async_api.async_playwright") as mock_playwright_fn:
        mock_playwright = MagicMock()
        mock_playwright.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.stop = AsyncMock()
        mock_playwright_fn.return_value = mock_playwright

        # 初始化
        await browser_service.initialize()

        # 关闭
        await browser_service.close()

        # 验证
        assert browser_service.is_initialized is False
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()


@pytest.mark.asyncio
async def test_browser_service_context_manager():
    """测试异步上下文管理器。"""
    config = BrowserConfig(headless=True)
    mock_browser = MagicMock(spec=Browser)
    mock_browser.close = AsyncMock()

    with patch("playwright.async_api.async_playwright") as mock_playwright_fn:
        mock_playwright = MagicMock()
        mock_playwright.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.stop = AsyncMock()
        mock_playwright_fn.return_value = mock_playwright

        async with BrowserService(config) as service:
            assert service.is_initialized is True

        # 退出上下文后应该关闭
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()


# ============================================================================
# 全局函数测试
# ============================================================================


@pytest.mark.asyncio
async def test_get_global_browser_service_singleton():
    """测试全局浏览器服务单例模式。"""
    # 重置全局变量
    import browser_service
    browser_service._global_browser_service = None

    # 第一次获取
    service1 = await get_global_browser_service()
    # 第二次获取
    service2 = await get_global_browser_service()

    # 应该是同一个实例
    assert service1 is service2

    # 清理
    browser_service._global_browser_service = None


@pytest.mark.asyncio
async def test_initialize_global_browser():
    """测试初始化全局浏览器。"""
    # 重置全局变量
    import browser_service
    browser_service._global_browser_service = None

    with patch("playwright.async_api.async_playwright") as mock_playwright_fn:
        mock_playwright = MagicMock()
        mock_playwright.start = AsyncMock(return_value=mock_playwright)
        mock_browser = MagicMock(spec=Browser)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright_fn.return_value = mock_playwright

        # 初始化
        await initialize_global_browser()

        # 验证
        service = await get_global_browser_service()
        assert service.is_initialized is True

        # 清理
        browser_service._global_browser_service = None


@pytest.mark.asyncio
async def test_close_global_browser():
    """测试关闭全局浏览器。"""
    # 重置全局变量
    import browser_service
    browser_service._global_browser_service = None

    with patch("playwright.async_api.async_playwright") as mock_playwright_fn:
        mock_playwright = MagicMock()
        mock_playwright.start = AsyncMock(return_value=mock_playwright)
        mock_browser = MagicMock(spec=Browser)
        mock_browser.close = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.stop = AsyncMock()
        mock_playwright_fn.return_value = mock_playwright

        # 初始化
        await initialize_global_browser()

        # 关闭
        await close_global_browser()

        # 验证
        service = await get_global_browser_service()
        assert service.is_initialized is False
        mock_browser.close.assert_called_once()

        # 清理
        browser_service._global_browser_service = None


# ============================================================================
# 异常测试
# ============================================================================


def test_browser_error():
    """测试 BrowserError 异常。"""
    error = BrowserError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_page_creation_error():
    """测试 PageCreationError 异常。"""
    error = PageCreationError("Failed to create page")
    assert str(error) == "Failed to create page"
    assert isinstance(error, BrowserError)


def test_page_closed_error():
    """测试 PageClosedError 异常。"""
    error = PageClosedError("Page is closed")
    assert str(error) == "Page is closed"
    assert isinstance(error, BrowserError)


def test_browser_initialization_error():
    """测试 BrowserInitializationError 异常。"""
    error = BrowserInitializationError("Failed to initialize")
    assert str(error) == "Failed to initialize"
    assert isinstance(error, BrowserError)


# ============================================================================
# 并发测试
# ============================================================================


@pytest.mark.asyncio
async def test_page_pool_concurrent_access():
    """测试页面池并发访问。"""
    # 创建模拟
    mock_browser = MagicMock(spec=Browser)
    mock_stealth = MagicMock()
    mock_stealth.apply_stealth_async = AsyncMock()

    config = BrowserConfig(max_cached_pages=2)
    pool = PagePool(mock_browser, mock_stealth, config)

    # 创建多个模拟页面
    mock_pages = []
    for i in range(5):
        mock_context = MagicMock(spec=BrowserContext)
        mock_page = MagicMock(spec=Page)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_pages.append((mock_context, mock_page))

    mock_browser.new_context = AsyncMock(side_effect=[mc for mc, _ in mock_pages])

    # 并发获取页面
    tasks = [pool.acquire() for _ in range(5)]
    pages = await asyncio.gather(*tasks)

    # 验证获取了5个页面
    assert len(pages) == 5
    assert len(pool._pool) == 5

    # 验证所有页面都被标记为使用中
    for pooled in pool._pool:
        assert pooled.in_use is True
