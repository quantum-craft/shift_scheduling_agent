"""HRM 的 自訂群組相關 API"""

import httpx
from typing import List
from pydantic import BaseModel, Field
from uuid import UUID
from hrm.webapi.unified.response import WebAPIResponse
from hrm.webapi.unified.urlutils import *
from http import HTTPStatus


class GroupInfo(BaseModel):
    """自訂群組資料模型"""
    group_id: UUID = Field(..., alias="groupId")
    group_name: str = Field(..., alias="groupName")


async def get_custom_group_info(token: str) -> WebAPIResponse[GroupInfo]:
    """
    取得自訂群組清單.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        自訂群組清單
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        full_url = get_hrm_tool_full_endpoint("api/groups/customs")
        response = await client.get(full_url, headers=my_headers)
        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}")
            response.raise_for_status()
        response_model = WebAPIResponse[List[GroupInfo]](**response.json())
        return response_model
