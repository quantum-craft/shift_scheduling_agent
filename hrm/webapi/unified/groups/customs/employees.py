"""HRM 的 自訂群組相關 API"""

import httpx
from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from hrm.webapi.unified.response import WebAPIResponse
from hrm.webapi.unified.urlutils import *
from http import HTTPStatus


class GroupEmployeeInfo(BaseModel):
    """自訂群組人員資料模型"""
    group_id: UUID = Field(..., alias="groupId")
    employee_ids: List[UUID] = Field(..., alias="employeeIds")


async def get_employees_info(token: str) -> WebAPIResponse[GroupEmployeeInfo]:
    """
    取得自訂群組員工清單.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        自訂群組員工清單
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        full_url = get_hrm_tool_full_endpoint("api/groups/customs/employees")
        response = await client.get(full_url, headers=my_headers)
        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}")
            response.raise_for_status()
        response_model = WebAPIResponse[List[GroupEmployeeInfo]](
            **response.json())
        return response_model
