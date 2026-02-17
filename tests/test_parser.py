"""HTML 解析器模块的测试。"""

import pytest

from web_reader.models import WebReaderInput


@pytest.mark.asyncio
async def test_extract_title(parser, sample_html):
    """测试标题提取。"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(sample_html, "html.parser")

    # 从 readabilipy 结果（模拟）
    article_json = {"title": "Introduction to Web Scraping"}
    title = parser._extract_title(article_json, soup)
    assert title == "Introduction to Web Scraping"


@pytest.mark.asyncio
async def test_extract_title_from_h1(parser, sample_html_simple):
    """测试当 JSON 中没有标题时从 h1 提取标题。"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(sample_html_simple, "html.parser")
    article_json = {}

    title = parser._extract_title(article_json, soup)
    assert title == "Hello World"


@pytest.mark.asyncio
async def test_extract_summary_from_meta(parser, sample_html):
    """测试从 meta description 提取摘要。"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(sample_html, "html.parser")
    summary = parser._extract_summary(soup)

    assert "test article about web scraping" in summary.lower()


@pytest.mark.asyncio
async def test_extract_summary_from_first_p(parser, sample_html_simple):
    """测试从第一段提取摘要。"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(sample_html_simple, "html.parser")
    summary = parser._extract_summary(soup)

    assert "simple test page" in summary.lower()


@pytest.mark.asyncio
async def test_truncate_summary(parser):
    """测试摘要截断。"""
    long_text = "This is a very long summary that should be truncated to a maximum length. " * 10

    result = parser._truncate_summary(long_text, max_length=50)

    assert len(result) <= 53  # 50 + "..."
    assert result.endswith("...")


@pytest.mark.asyncio
async def test_html_to_markdown(parser, sample_html):
    """测试 HTML 到 Markdown 的转换。"""
    markdown = parser._html_to_markdown(sample_html, retain_images=True)

    assert "# Introduction to Web Scraping" in markdown
    assert "## What is Web Scraping?" in markdown
    assert "* Automated data collection" in markdown or "- Automated data collection" in markdown


@pytest.mark.asyncio
async def test_html_to_text(parser, sample_html):
    """测试 HTML 到纯文本的转换。"""
    text = parser._html_to_text(sample_html)

    assert "Introduction to Web Scraping" in text
    assert "Web scraping is a powerful technique" in text


@pytest.mark.asyncio
async def test_extract_metadata(parser, sample_html):
    """测试元数据提取。"""
    metadata = parser._extract_metadata(sample_html, "content text", "summary text")

    assert metadata["author"] == "John Doe"
    assert "publish_date" in metadata
    assert metadata["word_count"] == 2  # "content text"
    assert metadata["og_title"] == "Test Article"


@pytest.mark.asyncio
async def test_parse_full(parser, sample_html):
    """测试完整解析流程。"""
    input_options = WebReaderInput(
        url="https://example.com/test",
        return_format="markdown",
        retain_images=True,
    )

    result = await parser.parse(sample_html, "https://example.com/test", input_options)

    assert result.success is True
    assert result.url == "https://example.com/test"
    # readabilipy 提取并处理标题
    assert result.title in ["Test Article", "Test Article - My Blog", "Introduction to Web Scraping"]
    assert "web scraping" in result.summary.lower() or "test article" in result.summary.lower()
    assert "# Introduction to Web Scraping" in result.content
    assert result.metadata["author"] == "John Doe"


@pytest.mark.asyncio
async def test_parse_with_text_format(parser, sample_html):
    """测试使用 text 格式而不是 markdown 进行解析。"""
    input_options = WebReaderInput(
        url="https://example.com/test",
        return_format="text",
        retain_images=False,
    )

    result = await parser.parse(sample_html, "https://example.com/test", input_options)

    assert result.success is True
    # 不应有 markdown 标题
    assert "#" not in result.content.split("\n")[0]
