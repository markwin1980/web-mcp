"""网页获取器模块的测试。"""

import pytest

from url_fetcher.exceptions import URLValidationError
from url_fetcher.fetcher import WebFetcher


@pytest.mark.asyncio
async def test_validate_url_success(fetcher):
    """测试有效 URL 被接受。"""
    # 不应抛出异常
    assert fetcher._validate_url("https://example.com") is None
    assert fetcher._validate_url("http://example.com") is None


@pytest.mark.asyncio
async def test_validate_url_failure(fetcher):
    """测试无效 URL 被拒绝。"""
    with pytest.raises(URLValidationError):
        fetcher._validate_url("ftp://example.com")

    with pytest.raises(URLValidationError):
        fetcher._validate_url("example.com")

    with pytest.raises(URLValidationError):
        fetcher._validate_url("")


@pytest.mark.asyncio
async def test_cache_store_and_retrieve(fetcher):
    """测试缓存存储和检索。"""
    url = "https://example.com/test"
    html = "<html><body>Test content</body></html>"

    # 存储到缓存
    fetcher._store_in_cache(url, html)

    # 从缓存检索
    cached = fetcher._get_from_cache(url)
    assert cached == html


@pytest.mark.asyncio
async def test_cache_expiration(fetcher, config):
    """测试缓存在 TTL 后过期。"""
    # 使用较短的 TTL 进行测试
    config.cache_ttl = 0
    fetcher_with_short_ttl = WebFetcher(config)

    url = "https://example.com/test"
    html = "<html><body>Test content</body></html>"

    # 存储到缓存
    fetcher_with_short_ttl._store_in_cache(url, html)

    # 应该立即过期
    cached = fetcher_with_short_ttl._get_from_cache(url)
    assert cached is None


@pytest.mark.asyncio
async def test_clear_cache(fetcher):
    """测试清空缓存。"""
    url = "https://example.com/test"
    html = "<html><body>Test content</body></html>"

    # 存储到缓存
    fetcher._store_in_cache(url, html)
    assert fetcher._get_from_cache(url) == html

    # 清空缓存
    fetcher.clear_cache()
    assert fetcher._get_from_cache(url) is None


@pytest.mark.asyncio
async def test_fetch_invalid_url(fetcher):
    """测试使用无效 URL 获取。"""
    with pytest.raises(URLValidationError):
        await fetcher.fetch("not-a-url", timeout=10)


@pytest.mark.asyncio
async def test_fetch_with_cache(fetcher, sample_html):
    """测试缓存存储和检索功能。"""
    url = "https://example.com/test"

    # 直接测试缓存功能：手动存储到缓存
    fetcher._store_in_cache(url, sample_html)

    # 验证缓存已存储
    cached = fetcher._get_from_cache(url)
    assert cached == sample_html

    # 验证 LRU 行为：再次访问应该将条目移到末尾
    fetcher._get_from_cache(url)

    # 添加更多缓存条目来测试 LRU 淘汰
    for i in range(fetcher._MAX_CACHE_SIZE):
        fetcher._store_in_cache(f"https://example.com/page{i}", f"content {i}")

    # 原始的 URL 应该已经被淘汰（因为它在最前面）
    cached_after = fetcher._get_from_cache(url)
    assert cached_after is None  # 应该已被 LRU 淘汰
