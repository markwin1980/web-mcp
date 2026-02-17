"""BaiduSearchClient 单元测试。"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from web_search.client import (
    BaiduSearchClient,
    BaiduSearchError,
    BaiduSearchAuthError,
    BaiduSearchAPIError,
)
from web_search.config import BaiduSearchConfig


@pytest.fixture
def mock_config():
    """提供测试配置。"""
    return BaiduSearchConfig(
        api_key="test-api-key",
        base_url="https://api.example.com/search",
        timeout=5,
        max_retries=2,
    )


@pytest.fixture
def client(mock_config):
    """提供百度搜索客户端实例。"""
    return BaiduSearchClient(mock_config)


@pytest.fixture
def sample_api_response():
    """提供百度 API 示例响应。"""
    return {
        "references": [
            {
                "id": 1,
                "type": "web",
                "title": "测试标题 1",
                "url": "https://example.com/1",
                "content": "这是测试内容 1",
                "date": "2025-01-15",
                "website": "example.com",
                "rerank_score": 0.95,
                "authority_score": 0.85,
            },
            {
                "id": 2,
                "type": "web",
                "title": "测试标题 2",
                "url": "https://example.com/2",
                "content": "这是测试内容 2",
                "date": "2025-01-16",
                "website": "example.com",
                "rerank_score": 0.85,
                "authority_score": 0.75,
            },
        ],
        "request_id": "test-request-id",
    }


@pytest.fixture
def mock_session():
    """提供模拟的 aiohttp 会话。"""
    session = MagicMock()
    response = AsyncMock()
    response.status = 200
    response.raise_for_status = MagicMock()
    response.json = AsyncMock()
    session.post = AsyncMock(return_value=response)
    return session, response


# ============================================================================
# 初始化测试
# ============================================================================

class TestBaiduSearchClientInit:
    """测试 BaiduSearchClient 初始化。"""

    def test_init_with_config(self, mock_config):
        """测试使用配置初始化。"""
        client = BaiduSearchClient(mock_config)
        assert client.config == mock_config

    def test_init_without_config(self):
        """测试不使用配置初始化（从环境变量读取）。"""
        with patch("web_search.client.BaiduSearchConfig.from_env") as mock_from_env:
            mock_from_env.return_value = BaiduSearchConfig(api_key="env-key")
            client = BaiduSearchClient(None)
            mock_from_env.assert_called_once()
            assert client.config.api_key == "env-key"


# ============================================================================
# 会话管理测试
# ============================================================================

class TestBaiduSearchClientSession:
    """测试会话管理功能。"""

    @pytest.mark.asyncio
    async def test_ensure_session_creates_new(self, client):
        """测试创建新会话。"""
        session = await client._ensure_session()
        assert session is not None
        assert isinstance(session, aiohttp.ClientSession)
        await client.close()

    @pytest.mark.asyncio
    async def test_ensure_session_reuses_existing(self, client):
        """测试重用现有会话。"""
        session1 = await client._ensure_session()
        session2 = await client._ensure_session()
        assert session1 is session2
        await client.close()

    @pytest.mark.asyncio
    async def test_close_closes_session(self, client):
        """测试关闭会话。"""
        session = await client._ensure_session()
        await client.close()
        assert session.closed

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config):
        """测试异步上下文管理器。"""
        async with BaiduSearchClient(mock_config) as client:
            session = await client._ensure_session()
            assert not session.closed
        assert session.closed


# ============================================================================
# 搜索功能测试
# ============================================================================

class TestBaiduSearchClientSearch:
    """测试搜索功能。"""

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_search_success(self, mock_post, client, sample_api_response):
        """测试成功搜索。"""
        # 设置 mock 响应
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=sample_api_response)
        mock_post.return_value.__aenter__.return_value = mock_response

        # 执行搜索
        results = await client.search("测试查询", num_results=5)

        # 验证结果
        assert len(results) == 2
        assert results[0]["title"] == "测试标题 1"
        assert results[0]["url"] == "https://example.com/1"
        assert results[0]["snippet"] == "这是测试内容 1"
        assert results[0]["rank"] == 1

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_search_request_body(self, mock_post, client, sample_api_response):
        """测试请求体构建。"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=sample_api_response)
        mock_post.return_value.__aenter__.return_value = mock_response

        await client.search("测试查询", num_results=30)

        # 验证请求参数
        call_args = mock_post.call_args
        assert call_args[0][0] == client.config.base_url

        # 验证请求头
        headers = call_args[1]["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["X-Appbuilder-Authorization"] == "Bearer test-api-key"

        # 验证请求体
        json_data = call_args[1]["json"]
        assert json_data["messages"][0]["content"] == "测试查询"
        assert json_data["messages"][0]["role"] == "user"
        assert json_data["search_source"] == "baidu_search_v2"
        assert json_data["resource_type_filter"][0]["type"] == "web"
        assert json_data["resource_type_filter"][0]["top_k"] == 30

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_search_top_k_limits_to_50(self, mock_post, client, sample_api_response):
        """测试 top_k 限制为 50。"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=sample_api_response)
        mock_post.return_value.__aenter__.return_value = mock_response

        await client.search("测试查询", num_results=100)

        json_data = mock_post.call_args[1]["json"]
        assert json_data["resource_type_filter"][0]["top_k"] == 50

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_search_with_429_retry(self, mock_post, client, sample_api_response):
        """测试 429 限流重试。"""
        # 第一次返回 429，第二次成功
        mock_response_429 = AsyncMock()
        mock_response_429.status = 429

        mock_response_success = AsyncMock()
        mock_response_success.status = 200
        mock_response_success.raise_for_status = MagicMock()
        mock_response_success.json = AsyncMock(return_value=sample_api_response)

        mock_post.return_value.__aenter__.side_effect = [
            mock_response_429,
            mock_response_success,
        ]

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            results = await client.search("测试查询")
            assert len(results) == 2
            mock_sleep.assert_called_once()

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_search_with_401_raises_auth_error(self, mock_post, client):
        """测试 401 认证失败抛出认证错误。"""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(BaiduSearchAuthError) as exc_info:
            await client.search("测试查询")

        assert "认证失败" in str(exc_info.value)
        assert "BAIDU_API_KEY" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_search_with_client_error_raises_after_retries(self, mock_post, client):
        """测试网络错误重试后抛出异常。"""
        mock_post.side_effect = aiohttp.ClientError("连接失败")

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            with pytest.raises(BaiduSearchError) as exc_info:
                await client.search("测试查询")

            assert mock_sleep.call_count == client.config.max_retries - 1
            assert "调用失败" in str(exc_info.value)
            assert "重试" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_search_with_json_decode_error(self, mock_post, client):
        """测试 JSON 解析错误。"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(side_effect=json.JSONDecodeError("无效 JSON", "", 0))
        mock_post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(BaiduSearchError):
            await client.search("测试查询")


# ============================================================================
# 响应解析测试
# ============================================================================

class TestBaiduSearchClientParseResponse:
    """测试响应解析功能。"""

    def test_parse_response_success(self, client, sample_api_response):
        """测试成功解析响应。"""
        results = client._parse_response(sample_api_response, "测试查询")
        assert len(results) == 2
        assert results[0]["title"] == "测试标题 1"
        assert results[0]["url"] == "https://example.com/1"
        assert results[0]["snippet"] == "这是测试内容 1"
        assert results[0]["date"] == "2025-01-15"
        assert results[0]["website"] == "example.com"
        assert results[0]["rerank_score"] == 0.95
        assert results[0]["authority_score"] == 0.85
        assert results[0]["rank"] == 1

    def test_parse_response_with_error_code(self, client):
        """测试解析带错误码的响应。"""
        error_response = {
            "code": "216003",
            "message": "Authentication error",
        }
        with pytest.raises(BaiduSearchAPIError) as exc_info:
            client._parse_response(error_response, "测试查询")

        assert "216003" in str(exc_info.value)
        assert "Authentication error" in str(exc_info.value)

    def test_parse_response_empty_references(self, client):
        """测试解析空 references。"""
        empty_response = {"references": [], "request_id": "test-id"}
        results = client._parse_response(empty_response, "测试查询")
        assert len(results) == 0

    def test_parse_response_no_references(self, client):
        """测试解析没有 references 字段。"""
        no_ref_response = {"request_id": "test-id"}
        results = client._parse_response(no_ref_response, "测试查询")
        assert len(results) == 0

    def test_parse_response_with_exception(self, client):
        """测试解析异常。"""
        # 传入无效数据
        with pytest.raises(BaiduSearchError):
            client._parse_response(None, "测试查询")  # type: ignore


# ============================================================================
# Reference 解析测试
# ============================================================================

class TestBaiduSearchClientParseReference:
    """测试单个 reference 解析。"""

    def test_parse_reference_web(self, client):
        """测试解析网页类型 reference。"""
        ref = {
            "type": "web",
            "title": "测试标题",
            "url": "https://example.com",
            "content": "测试内容",
            "date": "2025-01-15",
            "website": "example.com",
            "rerank_score": 0.9,
            "authority_score": 0.8,
        }
        result = client._parse_reference(ref, 1)
        assert result is not None
        assert result["title"] == "测试标题"
        assert result["url"] == "https://example.com"
        assert result["snippet"] == "测试内容"
        assert result["date"] == "2025-01-15"
        assert result["website"] == "example.com"
        assert result["rerank_score"] == 0.9
        assert result["authority_score"] == 0.8
        assert result["rank"] == 1

    def test_parse_reference_non_web(self, client):
        """测试解析非网页类型 reference。"""
        ref = {
            "type": "video",
            "title": "视频标题",
            "url": "https://example.com/video",
        }
        result = client._parse_reference(ref, 1)
        assert result is None

    def test_parse_reference_missing_title(self, client):
        """测试解析缺少标题的 reference。"""
        ref = {
            "type": "web",
            "url": "https://example.com",
            "content": "测试内容",
        }
        result = client._parse_reference(ref, 1)
        assert result is None

    def test_parse_reference_missing_url(self, client):
        """测试解析缺少 URL 的 reference。"""
        ref = {
            "type": "web",
            "title": "测试标题",
            "content": "测试内容",
        }
        result = client._parse_reference(ref, 1)
        assert result is None

    def test_parse_reference_with_exception(self, client):
        """测试解析异常。"""
        # 传入无效数据
        result = client._parse_reference(None, 1)  # type: ignore
        assert result is None

    def test_parse_reference_missing_optional_fields(self, client):
        """测试解析缺少可选字段的 reference。"""
        ref = {
            "type": "web",
            "title": "测试标题",
            "url": "https://example.com",
            # 缺少其他字段
        }
        result = client._parse_reference(ref, 1)
        assert result is not None
        assert result["title"] == "测试标题"
        assert result["url"] == "https://example.com"
        assert result["snippet"] == ""
        assert result["date"] == ""
        assert result["website"] == ""
        assert result["rerank_score"] == 0.0
        assert result["authority_score"] == 0.0
