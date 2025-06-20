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


async def delete_department_schedules(
    token: str, departmentId: UUID, startDate: str, endDate: str
):
    """
    刪除部門行事曆排班紀錄.

    根據 API Spec: DELETE /api/calendars/departments/{departmentId}
    Query Parameters: startDate (string, date), endDate (string, date)
    Response: BooleanAPIResponse (data: bool, message: str)

    :param token: Bearer Token 驗證資訊
    :param departmentId: 部門 Id (UUID)
    :param startDate: 開始日期 (YYYY-MM-DD)
    :param endDate: 結束日期 (YYYY-MM-DD)
    :raises: HTTPStatusError 當 API 回傳非 200 時
    """
    async with httpx.AsyncClient() as client:
        my_headers = {"Authorization": token}

        # 構建包含 departmentId 的 URL
        base_url = get_hrm_tool_full_endpoint(
            f"api/calendars/departments/{str(departmentId)}"
        )

        # 準備查詢參數
        query_params = {
            "startDate": startDate,
            "endDate": endDate
        }

        response = await client.delete(
            base_url, headers=my_headers, params=query_params
        )

        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}, 回應內容: {response.text}")
            response.raise_for_status()
