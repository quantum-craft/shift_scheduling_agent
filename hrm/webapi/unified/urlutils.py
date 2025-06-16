"""url工具"""

from urllib.parse import urljoin
from hrm.webapi.unified.env import *
from functools import lru_cache


@lru_cache(maxsize=2)
def get_hrm_tool_full_endpoint(route: str) -> str:
    """取得 HRM 工具完整路徑"""
    base_url = get_hrm_tool_endpoint()
    route = route.lstrip('/')
    full_url = urljoin(base_url, route)
    return full_url
