"""浏览器服务模块的集成测试（使用真实浏览器）。"""

import pytest

from browser_service import (
    initialize_global_browser,
    close_global_browser,
    get_global_browser_service,
)


@pytest.mark.asyncio
async def test_browser_service_create_page():
    """测试创建页面。"""
    await initialize_global_browser()

    browser_service = await get_global_browser_service()
    # 创建页面
    page = await browser_service.create_page()
    # 验证
    assert page is not None
    # 清理：释放页面
    await browser_service.release_page(page)

    await close_global_browser()


@pytest.mark.asyncio
async def test_browser_service_multiple_pages():
    """测试创建多个页面。"""
    await initialize_global_browser()

    browser_service = await get_global_browser_service()
    pages = []
    # 创建多个页面
    for _ in range(3):
        page = await browser_service.create_page()
        assert page is not None
        pages.append(page)

    # 清理：释放所有页面
    for page in pages:
        await browser_service.release_page(page)

    await close_global_browser()
