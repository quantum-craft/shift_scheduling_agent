"""HRM 的 排班記錄相關 API"""

import httpx
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
from datetime import date as datetype
from uuid import UUID
from hrm.webapi.unified.response import WebAPIResponse
from hrm.webapi.unified.urlutils import *
from http import HTTPStatus
import json
from enum import Enum


class WorkStatusEnum(int, Enum):
    ON_DUTY = 0
    OFF_DUTY = 1
    LEAVE = 2
    # 可依實際支援狀態補充


class DateTimeRange(BaseModel):
    start: datetime = Field(..., description="起始時間")
    end: datetime = Field(..., description="結束時間")


class EmployeeScheduledRecordViewModel(BaseModel):
    """
    員工排班紀錄資料
    """

    employeeNumber: str = Field(..., description="員工工號")
    workStatusCode: WorkStatusEnum = Field(..., description="工作狀態代碼")
    shiftScheduleCode: str = Field(..., description="班次代碼")
    date: datetype = Field(..., description="排班日期")
    workTime: DateTimeRange = Field(..., description="工作時間區間")
    restTimes: Optional[List[DateTimeRange]] = Field(
        None, description="休息時間清單")


async def update_employee_schedules(token: str, records: List[EmployeeScheduledRecordViewModel]) -> WebAPIResponse[object]:
    """
    更新指定員工排班。

    :param token: Bearer Token 驗證資訊
    :param records: 員工排班紀錄清單
    :raises: HTTPStatusError 當 API 回傳非 200 時
    :return: ObjectAPIResponse 包裝的結果
    """

    async with httpx.AsyncClient() as client:
        my_headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

        base_url = get_hrm_tool_full_endpoint(
            "api/scheduled-records/departments")

        # 將 Pydantic 模型列表轉換為適合 JSON 序列化的字典列表。
        # Pydantic v2: record.model_dump(mode="json")
        # Pydantic v1: json.loads(record.json())
        # 這裡假設您使用的是 Pydantic v2 或更高版本。
        # mode="json" 確保 date/datetime 等類型被正確轉換為 JSON 相容的字串。
        payload = [record.model_dump(mode="json") for record in records]

        print(payload)
        # 使用 httpx 的 `json` 參數將 payload 作為請求主體傳送。
        # httpx 會自動將 Python 字典/列表序列化為 JSON 字串。
        response = await client.put(base_url, headers=my_headers, json=payload)

        if response.status_code != HTTPStatus.OK:
            print(f"請求失敗，狀態碼: {response.status_code}, 回應內容: {response.text}")
            response.raise_for_status()

        # 嘗試解析回應的 JSON，如果 API 可能回傳非 JSON 或空回應，則進行處理
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            # 如果 API 在成功時可能回傳空內容或非 JSON 內容
            if response.status_code == HTTPStatus.OK and not response.content:
                # 假設成功但無特定資料回傳
                response_data = {"isSuccess": True, "message": "Operation successful, no content returned.",
                                 "data": None, "traceId": response.headers.get("traceId")}
            else:
                print(f"API 回應不是有效的 JSON: {response.text}")
                raise  # 或者更優雅地處理這個錯誤

        response_model = WebAPIResponse[object](**response_data)
        return response_model
