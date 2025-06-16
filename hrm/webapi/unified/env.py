"""環境變數"""

import os
from functools import lru_cache


@lru_cache(maxsize=2)
def get_hrm_tool_endpoint() -> str:
    """取得HRM工具存取位置"""
    base_url = os.getenv("HRM_TOOL_ENDPOINT")

    if not base_url:
        raise ValueError("環境變數 HRM_TOOL_ENDPOINT 未設定或為空值")

    base_url = f"{base_url.rstrip('/')}/"
    return base_url
