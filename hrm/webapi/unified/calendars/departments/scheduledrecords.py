"""HRM 的 部門行事曆相關 API"""

import httpx
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
from datetime import date as datetype
from uuid import UUID
from hrm.webapi.unified.response import WebAPIResponse
from hrm.webapi.unified.urlutils import *
from http import HTTPStatus


class DateTimeRange(BaseModel):
    """日期時間區間"""
    start: datetime = Field(..., alias="start", description="起始時間")
    end: datetime = Field(..., alias="end", description="結束時間")


class WorkRecordShiftSchedule(BaseModel):
    """工作班表排班"""
    work_time_range: DateTimeRange = Field(...,
                                           alias="workTimeRange", description="工作時間區間")
    rest_time_ranges: List[DateTimeRange] = Field(
        ..., alias="restTimeRanges", description="休息時間區間清單")
    shift_schedule_id: UUID = Field(...,
                                    alias="shiftScheduleId", description="班表 ID")


class WorkRecord(BaseModel):
    """工作紀錄"""
    date: datetype = Field(..., alias="date", description="紀錄日期（僅日期）")
    is_editable: bool = Field(..., alias="isEditable", description="是否可編輯")
    work_record_shift_schedules: List[WorkRecordShiftSchedule] = Field(
        ..., alias="workRecordShiftSchedules", description="班表安排")


class HolidayRecord(BaseModel):
    """假日紀錄"""
    date: datetype = Field(..., alias="date", description="假日日期（僅日期）")
    holiday_type: str = Field(..., alias="holidayType", description="假日類型")
    is_editable: bool = Field(..., alias="isEditable", description="是否可編輯")


class EmployeeRecordViewModel(BaseModel):
    """員工工作與假日狀態"""
    employee_id: UUID = Field(..., alias="employeeId", description="員工 ID")
    work_records: List[WorkRecord] = Field(...,
                                           alias="workRecords", description="工作紀錄清單")
    holiday_records: List[HolidayRecord] = Field(
        ..., alias="holidayRecords", description="假日紀錄清單")


class DepartmentCalendarViewModel(BaseModel):
    """部門行事曆資訊"""
    department_id: UUID = Field(..., alias="departmentId", description="部門 ID")
    employees: List[EmployeeRecordViewModel] = Field(
        ..., alias="employees", description="員工工作狀態清單")


async def get_calendars(token: str, departmentId: UUID, startDate: str, endDate: str) -> WebAPIResponse[DepartmentCalendarViewModel]:
    """
    取得部門行事曆資訊.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        部門行事曆資訊
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        base_url = get_hrm_tool_full_endpoint(
            f"api/calendars/departments/{departmentId}/scheduled-records")

        query = f"startDate={startDate}&endDate={endDate}"

        full_url = f"{base_url}?{query}"

        response = await client.get(full_url, headers=my_headers)
        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}")
            response.raise_for_status()
        print(response.json())
        response_model = WebAPIResponse[DepartmentCalendarViewModel](
            **response.json())
        return response_model
