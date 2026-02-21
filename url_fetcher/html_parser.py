"""解析 Readability.js 的输出并转换为 Markdown。"""

import re
from typing import Any

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter

from url_fetcher.exceptions import ParseError


class HTMLParser:
    """解析 Readability.js 的输出。"""

    def parse(
        self,
        article: dict,
        url: str,
        return_format: str = "markdown",
    ) -> dict[str, Any]:
        """解析 Readability.js 的文章数据。

        Args:
            article: Readability.js 返回的字典
            url: 原始 URL
            return_format: 返回格式 ("markdown" 或 "text")

        Returns:
            包含解析结果的字典
        """
        try:
            if not article:
                raise ParseError("文章数据为空")

            # 从 Readability.js 输出中提取
            title = article.get("title", "无标题") or "无标题"
            content_html = article.get("content", "")
            summary = article.get("excerpt", "") or self._extract_summary(content_html)

            # 转换为 markdown 或 text（默认保留图片）
            if return_format == "markdown":
                content = self._html_to_markdown(content_html, retain_images=True)
            else:
                content = article.get("textContent", "") or self._html_to_text(content_html)

            # 提取元数据
            metadata = self._extract_metadata(article, content, summary)

            return {
                "url": url,
                "title": title.strip(),
                "summary": self._truncate_summary(summary),
                "content": content,
                "metadata": metadata,
            }

        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"解析文章失败：{e!s}")

    def _extract_summary(self, html: str) -> str:
        """从 HTML 中提取摘要（备用方案）。"""
        if not html:
            return "无可用摘要"
        soup = BeautifulSoup(html, "html.parser")
        first_p = soup.find("p")
        if first_p:
            return first_p.get_text().strip()
        return "无可用摘要"

    def _truncate_summary(self, text: str, max_length: int = 200) -> str:
        if not text:
            return "无可用摘要"
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def _html_to_markdown(self, html: str, retain_images: bool) -> str:
        strip_tags = [] if retain_images else ["img"]
        converter = MarkdownConverter(
            bullets="*",
            heading_style="ATX",
            strip=strip_tags,
        )
        markdown = converter.convert(html)
        markdown = re.sub(r"\n\n\n+", "\n\n", markdown)
        return markdown.strip()

    def _html_to_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        text = re.sub(r"\n\n\n+", "\n\n", text)
        return text.strip()

    def _extract_metadata(self, article: dict, content: str, summary: str) -> dict:
        """从 Readability.js 输出中提取元数据。"""
        metadata = {}

        # 作者
        if article.get("byline"):
            metadata["author"] = article["byline"]

        # 字数
        if article.get("length"):
            metadata["word_count"] = article["length"]
        else:
            metadata["word_count"] = len(content.split())

        # 站点名（如果有）
        if article.get("siteName"):
            metadata["site_name"] = article["siteName"]

        return metadata
