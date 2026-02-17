"""百度智能云千帆 AI 搜索 API 客户端。"""

import asyncio
import json
from typing import Any

import aiohttp

from .config import BaiduSearchConfig
from .exceptions import BaiduSearchError, BaiduSearchAuthError, BaiduSearchAPIError


class BaiduSearchClient:
    """百度智能云千帆 AI 搜索 API 客户端。"""

    def __init__(self, config: BaiduSearchConfig | None = None):
        """初始化千帆搜索客户端。

        Args:
            config: 千帆搜索配置，如果为 None 则从环境变量读取
        """
        self.config = config or BaiduSearchConfig.from_env()
        self._session: aiohttp.ClientSession | None = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """确保 aiohttp 会话已创建。"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """关闭会话。"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "BaiduSearchClient":
        """异步上下文管理器入口。"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口。"""
        await self.close()

    async def search(
        self,
        query: str,
        num_results: int = 10,
    ) -> list[dict[str, Any]]:
        """执行千帆 AI 搜索。

        Args:
            query: 搜索关键词
            num_results: 返回结果数量（最多50个）

        Returns:
            搜索结果列表，每个结果包含 title、url、snippet 等字段
        """
        session = await self._ensure_session()

        # 构建请求体
        top_k = min(num_results, 50)  # 网页搜索最多返回50个

        request_body = {
            "messages": [
                {
                    "content": query,
                    "role": "user"
                }
            ],
            "search_source": self.config.search_source,
            "resource_type_filter": [
                {
                    "type": "web",
                    "top_k": top_k
                }
            ],
        }

        headers = {
            "Content-Type": "application/json",
            "X-Appbuilder-Authorization": f"Bearer {self.config.api_key}",
        }

        last_exception = None

        for attempt in range(self.config.max_retries):
            try:
                async with session.post(
                    self.config.base_url,
                    json=request_body,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                ) as response:
                    if response.status == 429:
                        # 请求过于频繁，等待后重试
                        wait_time = 2 ** (attempt + 1)
                        await asyncio.sleep(wait_time)
                        continue

                    if response.status == 401:
                        raise BaiduSearchAuthError(
                            f"千帆 API 认证失败: {response.status}，请检查 BAIDU_API_KEY 是否正确"
                        )

                    response.raise_for_status()
                    data = await response.json()
                    return self._parse_response(data, query)

            except (BaiduSearchAuthError, BaiduSearchAPIError):
                # 认证错误和 API 错误直接抛出，不重试
                raise
            except aiohttp.ClientError as e:
                last_exception = e
                wait_time = 2 ** (attempt + 1)
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(wait_time)

            except json.JSONDecodeError as e:
                last_exception = e
                break

            except Exception as e:
                last_exception = e
                break

        # 所有重试都失败
        raise BaiduSearchError(
            f"千帆搜索 API 调用失败，已重试 {self.config.max_retries} 次: {last_exception}"
        )

    def _parse_response(
        self, data: dict[str, Any], query: str
    ) -> list[dict[str, Any]]:
        """解析千帆 AI 搜索 API 响应。"""
        results: list[dict[str, Any]] = []

        try:
            # 检查是否有错误
            if "code" in data and data["code"]:
                raise BaiduSearchAPIError(
                    f"千帆 API 返回错误: code={data.get('code')}, message={data.get('message')}"
                )

            # 解析 references
            references = data.get("references", [])

            for idx, ref in enumerate(references):
                result = self._parse_reference(ref, idx + 1)
                if result:
                    results.append(result)

        except BaiduSearchAPIError:
            raise
        except Exception as e:
            raise BaiduSearchError(f"解析千帆搜索响应失败: {e}") from e

        # 如果没有解析到结果，返回空列表
        if not results:
            return []

        return results

    def _parse_reference(self, ref: dict[str, Any], rank: int) -> dict[str, Any] | None:
        """解析单个 reference 对象。"""
        try:
            ref_type = ref.get("type", "web")

            # 只处理网页类型的结果
            if ref_type != "web":
                return None

            title = ref.get("title", "")
            url = ref.get("url", "")
            content = ref.get("content", "")
            date = ref.get("date", "")
            website = ref.get("website", "")
            rerank_score = ref.get("rerank_score", 0.0)
            authority_score = ref.get("authority_score", 0.0)

            if not title or not url:
                return None

            return {
                "title": title,
                "url": url,
                "snippet": content,
                "date": date,
                "website": website,
                "rerank_score": rerank_score,
                "authority_score": authority_score,
                "rank": rank,
            }

        except Exception:
            return None

