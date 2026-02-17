"""web-reader 的数据模型。"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class WebReaderInput:
    """webReader 工具的输入参数。"""

    url: str
    return_format: Literal["markdown", "text"] = "markdown"
    retain_images: bool = True
    timeout: int = 20
    no_cache: bool = False

    def __post_init__(self):
        """验证输入参数。"""
        # 验证 URL
        if not self.url.startswith(("http://", "https://")):
            raise ValueError("URL 必须以 http:// 或 https:// 开头")

        # 验证 timeout 范围
        if not (5 <= self.timeout <= 60):
            raise ValueError("timeout 必须在 5-60 之间")


@dataclass
class ParseResult:
    """解析网页的结果。"""

    url: str
    title: str
    summary: str
    content: str
    metadata: dict = field(default_factory=dict)
    success: bool = True

