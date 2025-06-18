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


class TimeRange(BaseModel):
    """時間區間"""
    start: time = Field(..., alias="start", description="開始時間")
    end: time = Field(..., alias="end", description="結束時間")


class Section(BaseModel):
    """作業區段"""
    work_time_ranges: List[TimeRange] = Field(
        ..., alias="workTimeRanges", description="工作時間區間")
    rest_time_ranges: List[TimeRange] = Field(
        ..., alias="restTimeRanges", description="休息時間區間")


class Cycle(BaseModel):
    """班次週期"""
    cycle_id: UUID = Field(..., alias="cycleId", description="週期 ID")
    cycle_status_type: int = Field(...,
                                   alias="cycleStatusType", description="週期狀態類型")
    cycle_serial_number: int = Field(...,
                                     alias="cycleSerialNumber", description="週期序號")
    over_time_interval_minutes: int = Field(
        ..., alias="overTimeIntervalMinutes", description="加班時間間隔（分鐘）")
    sections: List[Section] = Field(...,
                                    alias="sections", description="時間區段清單")


class ShiftScheduleWithCyclesViewModel(BaseModel):
    """含週期設定的班次資料"""
    shift_schedule_id: UUID = Field(...,
                                    alias="shiftScheduleId", description="班次 ID")
    cycles: List[Cycle] = Field(..., alias="cycles", description="班次週期清單")


async def get_cycles(token: str, ids: Optional[List[UUID]] = None) -> WebAPIResponse[List[ShiftScheduleWithCyclesViewModel]]:
    """
    取得班次循環清單.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        班次循環清單
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        base_url = get_hrm_tool_full_endpoint("api/shift-schedules/cycles")

        if ids:
            query = "&".join([f"ids={str(i)}" for i in ids])
            full_url = f"{base_url}?{query}"
        else:
            full_url = base_url

        response = await client.get(full_url, headers=my_headers)
        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}")
            response.raise_for_status()
        print(response.json())
        response_model = WebAPIResponse[List[ShiftScheduleWithCyclesViewModel]](
            **response.json())
        return response_model
