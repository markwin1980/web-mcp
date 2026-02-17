"""HTML 解析和 Markdown 转换模块。"""

import re

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter
from readabilipy import simple_json_from_html_string

from web_reader.exceptions import ParseError
from web_reader.models import ParseResult, WebReaderInput


class HTMLParser:
    """解析 HTML 并转换为 Markdown。"""

    def __init__(self):
        """初始化解析器。"""
        pass

    async def parse(self, html: str, url: str, options: WebReaderInput) -> ParseResult:
        """解析 HTML 内容并提取结构化数据。

        Args:
            html: 要解析的 HTML 内容
            url: 原始 URL
            options: 来自 WebReaderInput 的解析选项

        Returns:
            包含标题、摘要、内容和元数据的 ParseResult

        Raises:
            ParseError: 如果解析失败
        """
        try:
            # 使用 readabilipy 解析
            article_json = simple_json_from_html_string(
                html, use_readability=True, content_digests=False
            )

            if not article_json or article_json.get("error"):
                raise ParseError("提取可读内容失败")

            # 提取内容
            content_html = article_json.get("content", "")
            if not content_html:
                raise ParseError("未找到内容")

            # 使用 BeautifulSoup 解析
            soup = BeautifulSoup(content_html, "html.parser")

            # 提取标题
            title = self._extract_title(article_json, soup)

            # 提取摘要
            summary = self._extract_summary(soup)

            # 转换为 markdown 或 text
            if options.return_format == "markdown":
                content = self._html_to_markdown(content_html, options.retain_images)
            else:
                content = self._html_to_text(content_html)

            # 提取元数据
            metadata = self._extract_metadata(html, content, summary)

            return ParseResult(
                url=url,
                title=title,
                summary=summary,
                content=content,
                metadata=metadata,
                success=True,
            )

        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"解析 HTML 失败：{e!s}")

    def _extract_title(self, article_json: dict, soup: BeautifulSoup) -> str:
        """从文章中提取标题。

        Args:
            article_json: 从 readabilipy 解析的文章 JSON
            soup: BeautifulSoup 解析的 HTML

        Returns:
            提取的标题
        """
        # 优先尝试 readability 标题
        title = article_json.get("title", "")
        if title:
            return title.strip()

        # 尝试 h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()

        # 尝试 title 标签
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()

        return "无标题"

    def _extract_summary(self, soup: BeautifulSoup) -> str:
        """从内容中提取摘要。

        Args:
            soup: BeautifulSoup 解析的 HTML

        Returns:
            提取的摘要（最多 200 字符）
        """
        # 尝试查找 meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            summary = meta_desc["content"].strip()
            return self._truncate_summary(summary)

        # 获取第一段
        first_p = soup.find("p")
        if first_p:
            summary = first_p.get_text().strip()
            return self._truncate_summary(summary)

        return "无可用摘要"

    def _truncate_summary(self, text: str, max_length: int = 200) -> str:
        """将摘要截断到最大长度。

        Args:
            text: 要截断的文本
            max_length: 最大长度

        Returns:
            截断后的文本，必要时添加省略号
        """
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(" ", 1)[0] + "..."

    def _html_to_markdown(self, html: str, retain_images: bool) -> str:
        """将 HTML 转换为 Markdown。

        Args:
            html: 要转换的 HTML
            retain_images: 是否保留图片

        Returns:
            Markdown 格式的内容
        """
        # strip 参数需要一个要移除的标签列表，而不是布尔值
        strip_tags = [] if retain_images else ["img"]
        converter = MarkdownConverter(
            bullets="*",
            heading_style="ATX",
            strip=strip_tags,
        )
        markdown = converter.convert(html)

        # 清理多余的空白
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        return markdown.strip()

    def _html_to_text(self, html: str) -> str:
        """将 HTML 转换为纯文本。

        Args:
            html: 要转换的 HTML

        Returns:
            纯文本内容
        """
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        # 清理多余的空白
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _extract_metadata(self, original_html: str, content: str, summary: str) -> dict:
        """从 HTML 中提取元数据。

        Args:
            original_html: 原始 HTML 内容
            content: 提取的内容
            summary: 摘要

        Returns:
            元数据字典
        """
        soup = BeautifulSoup(original_html, "html.parser")

        metadata = {}

        # 作者
        author = soup.find("meta", attrs={"name": "author"})
        if author and author.get("content"):
            metadata["author"] = author["content"]

        # 发布日期（多种格式）
        for meta_name in ["article:published_time", "date", "publish_date", "citation_date"]:
            meta = soup.find("meta", attrs={"property": meta_name}) or soup.find(
                "meta", attrs={"name": meta_name}
            )
            if meta and meta.get("content"):
                metadata["publish_date"] = meta["content"]
                break

        # 字数统计
        word_count = len(content.split())
        metadata["word_count"] = word_count

        # 图片数量
        img_tags = soup.find_all("img")
        metadata["image_count"] = len(img_tags)

        # Open Graph 数据
        og_title = soup.find("meta", attrs={"property": "og:title"})
        if og_title and og_title.get("content"):
            metadata["og_title"] = og_title["content"]

        og_description = soup.find("meta", attrs={"property": "og:description"})
        if og_description and og_description.get("content"):
            metadata["og_description"] = og_description["content"]

        og_image = soup.find("meta", attrs={"property": "og:image"})
        if og_image and og_image.get("content"):
            metadata["og_image"] = og_image["content"]

        # 网站名称
        site_name = soup.find("meta", attrs={"property": "og:site_name"})
        if site_name and site_name.get("content"):
            metadata["site_name"] = site_name["content"]

        return metadata
