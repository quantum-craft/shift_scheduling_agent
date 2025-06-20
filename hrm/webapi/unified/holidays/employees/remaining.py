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


class EffectiveDateRange(BaseModel):
    """生效日期區間"""
    start: date = Field(..., alias="start", description="開始日期")
    end: date = Field(..., alias="end", description="結束日期")


class RemainingHolidayItem(BaseModel):
    """剩餘假日項目"""
    effective_range: EffectiveDateRange = Field(
        ..., alias="effectiveRange", description="生效期間")
    monthly_leave_days: int = Field(...,
                                    alias="monthlyLeaveDays", description="每月請假天數")
    recess_days: int = Field(..., alias="recessDays", description="休息日天數")
    regular_day_off_days: int = Field(...,
                                      alias="regularDayOffDays", description="例休日天數")
    national_holiday_days: int = Field(...,
                                       alias="nationalHolidayDays", description="國定假日天數")


class EmployeeRemainingHolidayViewModel(BaseModel):
    """員工剩餘假日資料"""
    employee_id: UUID = Field(..., alias="employeeId", description="員工 ID")
    remaining_holidays: List[RemainingHolidayItem] = Field(
        ..., alias="remainingHolidays", description="剩餘假期清單")


async def get_remainings(token: str, ids: Optional[List[UUID]], startDate: str, endDate: str) -> WebAPIResponse[List[EmployeeRemainingHolidayViewModel]]:
    """
    取得員工剩餘假日清單.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        員工剩餘假日清單
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        base_url = get_hrm_tool_full_endpoint(
            "api/holidays/employees/remaining")

        date_condition = f"startDate={startDate}&endDate={endDate}"
        if ids:
            query = "&".join([f"ids={str(i)}" for i in ids])
            full_url = f"{base_url}?{date_condition}&{query}"
        else:
            full_url = f"{base_url}?{query}"
        # print(full_url)
        response = await client.get(full_url, headers=my_headers)
        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}")
            response.raise_for_status()
        # print(response.json())
        response_model = WebAPIResponse[List[EmployeeRemainingHolidayViewModel]](
            **response.json())
        return response_model
