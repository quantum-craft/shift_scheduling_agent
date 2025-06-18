"""HRM 的 員工套用班別相關 API"""

import httpx
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID
from hrm.webapi.unified.response import WebAPIResponse
from hrm.webapi.unified.urlutils import *
from http import HTTPStatus
from datetime import time


class EmployeeShiftAssignmentViewModel(BaseModel):
    """員工班別指派資料"""
    employee_id: UUID = Field(..., alias="employeeId", description="員工 ID")
    effective_date: date = Field(..., alias="effectiveDate", description="生效日期")
    shift_id: UUID = Field(..., alias="shiftId", description="班別 ID")



async def get_employee_shifts(token: str, ids: Optional[List[UUID]], startDate: str, endDate: str) -> WebAPIResponse[List[EmployeeShiftAssignmentViewModel]]:
    """
    取得員工套用班別清單.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        員工套用班別清單
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        base_url = get_hrm_tool_full_endpoint(
            "api/employee-scheduling-rule-settings/shifts")

        date_condition = f"startDate={startDate}&endDate={endDate}"
        if ids:
            query = "&".join([f"ids={str(i)}" for i in ids])
            full_url = f"{base_url}?{date_condition}&{query}"
        else:
            full_url = f"{base_url}?{query}"

        response = await client.get(full_url, headers=my_headers)
        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}")
            response.raise_for_status()
        print(response.json())
        response_model = WebAPIResponse[List[EmployeeShiftAssignmentViewModel]](
            **response.json())
        return response_model
