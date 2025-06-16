"""HRM 的 員工相關 API"""

import httpx
from async_lru import alru_cache
from pydantic import BaseModel
from uuid import UUID
from hrm.webapi.unified.response import WebAPIResponse
from hrm.webapi.unified.urlutils import *
from http import HTTPStatus


class EmployeeInfo(BaseModel):
    """員工資料模型"""
    companyId: UUID
    """公司專區ID"""
    employeeId: UUID
    employeeNumber: str
    employeeName: str
    departmentId: UUID


@alru_cache(typed=True, ttl=60)
async def get_my_employee_info(token: str) -> WebAPIResponse[EmployeeInfo]:
    """
    取得個人使用者資訊.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        使用者個人資訊請求
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        full_url = get_hrm_tool_full_endpoint("api/employees/me")
        response = await client.get(full_url, headers=my_headers)
        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}")
            response.raise_for_status()
        response_model = WebAPIResponse[EmployeeInfo](**response.json())
        return response_model
