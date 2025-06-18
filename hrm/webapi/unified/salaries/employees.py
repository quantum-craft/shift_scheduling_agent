"""HRM 的 員工套用班別相關 API"""

import httpx
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID
from hrm.webapi.unified.response import WebAPIResponse
from hrm.webapi.unified.urlutils import *
from http import HTTPStatus


class MoneyAmount(BaseModel):
    """金額資料"""
    currency: int = Field(..., alias="currency", description="幣別")
    amount: int = Field(..., alias="amount", description="金額")


class SalaryAccountItem(BaseModel):
    """薪資帳戶項目"""
    salary_account_type: str = Field(...,
                                     alias="salaryAccountType", description="薪資帳戶類型")
    amount: MoneyAmount = Field(..., alias="amount", description="金額資訊")


class EmployeeSalarySettingViewModel(BaseModel):
    """員工薪資設定"""
    effective_date: date = Field(...,
                                 alias="effectiveDate", description="生效日期")
    employee_id: UUID = Field(..., alias="employeeId", description="員工 ID")
    salary_accounts: List[SalaryAccountItem] = Field(
        ..., alias="salaryAccounts", description="薪資帳戶清單")
    salary_category: int = Field(...,
                                 alias="salaryCategory", description="薪資分類")


async def get_employee_salaries(token: str, ids: Optional[List[UUID]], startDate: str, endDate: str) -> WebAPIResponse[List[EmployeeSalarySettingViewModel]]:
    """
    取得員工薪資資訊.

    :raises:
        HTTPStatusError: 驗證失敗

    Returns:
        員工薪資資訊
    """

    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}
        base_url = get_hrm_tool_full_endpoint(
            "api/salaries/employees")

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
        # print(response.json())
        response_model = WebAPIResponse[List[EmployeeSalarySettingViewModel]](
            **response.json())
        return response_model
