"""web-search 的配置管理。"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class BaiduSearchConfig:
    """百度智能云千帆 AI 搜索 API 配置。"""

    api_key: str
    """百度智能云 AppBuilder API Key"""

    base_url: str = "https://qianfan.baidubce.com/v2/ai_search/web_search"
    """千帆 AI 搜索 API 基础 URL"""

    timeout: int = 30
    """请求超时时间（秒）"""

    max_retries: int = 3
    """最大重试次数"""

    search_source: str = "baidu_search_v2"
    """搜索引擎版本，固定值：baidu_search_v2"""

    @classmethod
    def from_env(cls) -> "BaiduSearchConfig":
        """从环境变量创建配置。

        环境变量:
            BAIDU_API_KEY: 百度 AppBuilder API Key（必需）
        """
        load_dotenv()

        api_key = os.getenv("BAIDU_API_KEY")
        if not api_key:
            raise ValueError("BAIDU_API_KEY 环境变量未设置，请在 .env 文件中配置")

        return cls(api_key=api_key)
