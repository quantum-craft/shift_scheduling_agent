"""HRM 的 班次相關 API"""

import httpx
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID
from hrm.webapi.unified.response import WebAPIResponse
from hrm.webapi.unified.urlutils import *
from http import HTTPStatus
from datetime import time

class ShiftScheduleViewModel(BaseModel):
    """班次資料模型"""
    shift_schedule_id: UUID = Field(..., alias="shiftScheduleId", description="班次 ID")
    shift_schedule_code: str = Field(..., alias="shiftScheduleCode", description="班次代碼")
    shift_schedule_name: str = Field(..., alias="shiftScheduleName", description="班次名稱")
    shift_schedule_start_time: time = Field(..., alias="shiftScheduleStartTime", description="開始時間")


async def get_shiftschedules(token: str, ids: Optional[List[UUID]] = None) -> WebAPIResponse[List[ShiftScheduleViewModel]]:
    """
    取得班次清單.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        班次清單
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        base_url = get_hrm_tool_full_endpoint("api/shift-schedules")

        if ids:
            query = "&".join([f"ids={str(i)}" for i in ids])
            full_url = f"{base_url}?{query}"
        else:
            full_url = base_url

        response = await client.get(full_url, headers=my_headers)
        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}")
            response.raise_for_status()
        # print(response.json())
        response_model = WebAPIResponse[List[ShiftScheduleViewModel]](
            **response.json())
        return response_model
