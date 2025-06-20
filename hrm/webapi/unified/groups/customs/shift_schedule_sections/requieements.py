"""HRM 的 自訂群組相關 API"""

import httpx
from datetime import time
from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from hrm.webapi.unified.response import WebAPIResponse
from hrm.webapi.unified.urlutils import *
from http import HTTPStatus


class TimeRange(BaseModel):
    start: time
    end: time


class MinRequirement(BaseModel):
    time_range: TimeRange = Field(..., alias="timeRange")
    employee_amount: int = Field(..., alias="employeeAmount")


class GroupMinRequirement(BaseModel):
    group_id: UUID = Field(..., alias="groupId")
    min_requirements: List[MinRequirement] = Field(
        ..., alias="minRequirements")


async def get_requirements(token: str) -> WebAPIResponse[List[GroupMinRequirement]]:
    """
    取得自訂群組班次時段最低人力清單.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        自訂群組班次時段最低人力清單
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        full_url = get_hrm_tool_full_endpoint(
            "api/groups/customs/shift-schedule-sections/requirements")
        response = await client.get(full_url, headers=my_headers)
        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}")
            response.raise_for_status()
        response_model = WebAPIResponse[List[GroupMinRequirement]](
            **response.json())
        return response_model
