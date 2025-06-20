"""HRM 的 班別相關 API"""

import httpx
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID
from hrm.webapi.unified.response import WebAPIResponse
from hrm.webapi.unified.urlutils import *
from http import HTTPStatus


class ShiftViewModel(BaseModel):
    """班別資料"""
    shift_id: UUID = Field(..., alias="shiftId")
    shift_code: str = Field(..., alias="shiftCode")
    shift_name: str = Field(..., alias="shiftName")
    default_shift_schedule_id: UUID = Field(...,
                                            alias="defaultShiftScheduleId")
    candidate_shift_schedule_ids: List[UUID] = Field(
        ..., alias="candidateShiftScheduleIds")
    cycle_day: int = Field(..., alias="cycleDay")
    labor_holiday_calendar_id: UUID = Field(...,
                                            alias="laborHolidayCalendarId")
    shift_schedule_start_date: date = Field(...,
                                            alias="shiftScheduleStartDate")
    is_auto_gen_schedule: bool = Field(..., alias="isAutoGenSchedule")
    is_allow_delete: bool = Field(..., alias="isAllowDelete")
    is_enabled: bool = Field(..., alias="isEnabled")


async def get_shifts(token: str, ids: Optional[List[UUID]] = None) -> WebAPIResponse[List[ShiftViewModel]]:
    """
    取得班別清單.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        班別清單
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        base_url = get_hrm_tool_full_endpoint("api/shifts")

        if ids:
            query = "&".join([f"ids={str(i)}" for i in ids])
            full_url = f"{base_url}?{query}"
        else:
            full_url = base_url

        response = await client.get(full_url, headers=my_headers)
        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}")
            response.raise_for_status()
        response_model = WebAPIResponse[List[ShiftViewModel]](
            **response.json())
        return response_model
