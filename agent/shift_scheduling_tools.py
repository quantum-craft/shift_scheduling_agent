from langchain_core.tools import tool
from typing import Annotated
from datetime import datetime
from datetime import time
from datetime import timedelta
from pydantic import BaseModel, Field
from agent.cp_sat_model.solver_manager import SolverManager
from agent.cp_sat_model.worker import Worker
from agent.cp_sat_model.shift import Shift


solver_manager = SolverManager()


@tool
def get_current_datetime() -> datetime:
    """
    取得並回傳當前日期時間，供後續排程運算使用。

    Returns:
        datetime: 目前的日期與時間。
    """

    return datetime.now()


@tool
def setup_date_interval_for_shift_scheduling(
    start_date_time: Annotated[datetime, "排班表的起始日期時間"],
    end_date_time: Annotated[datetime, "排班表的結束日期時間"],
) -> str:
    """
    必須先用工具 get_current_datetime 取得當前的日期和時間，
    接著根據推斷出的開始與結束日期時間，設定排班最佳化工具的日期區間。

    Args:
        start_date_time (datetime): 排班表的起始日期時間。
        end_date_time (datetime): 排班表的結束日期時間。

    Returns:
        str: 操作結果訊息，例如 "日期區間設定成功" 或錯誤訊息。
    """

    ret_days = []
    current = start_date_time
    while current <= end_date_time:
        ret_days.append(current)
        current += timedelta(days=1)

    solver_manager.set_days(ret_days)

    return "排班最佳化工具的日期區間設定成功."


@tool
def setup_workers_for_shift_scheduling() -> str:
    """
    註冊員工清單至排班最佳化工具，以便後續排程使用。

    Returns:
        str: 操作結果訊息，例如 "員工設定成功" 或錯誤訊息。
    """

    solver_manager.set_workers(
        [
            Worker(worker_id="張三"),
            Worker(worker_id="李四"),
            Worker(worker_id="王五"),
            Worker(worker_id="趙六"),
        ]
    )

    return "排班最佳化工具的員工設定成功."


@tool
def setup_shifts_for_shift_scheduling() -> str:
    """
    註冊班次清單至排班最佳化工具，以便後續排程使用。

    Returns:
        str: 操作結果訊息，例如 "班次設定成功" 或錯誤訊息。
    """

    solver_manager.set_shifts(
        [
            Shift(
                id="早班",
                start_time=time(hour=9, minute=0, second=0),
                end_time=time(hour=18, minute=0, second=0),
            ),
            Shift(
                id="午班",
                start_time=time(hour=13, minute=0, second=0),
                end_time=time(hour=22, minute=0, second=0),
            ),
            Shift(
                id="晚班",
                start_time=time(hour=18, minute=0, second=0),
                end_time=time(hour=3, minute=0, second=0),
            ),
        ]
    )

    return "排班最佳化工具的班次設定成功."


@tool
def initialize_ortools() -> str:
    """
    初始化排班最佳化工具並回傳狀態結果。

    Returns:
        str: 初始設定結果訊息，例如 "初始化成功" 或錯誤訊息。
    """

    status, init_ok = solver_manager.init()

    return status


shift_scheduling_tool_list = [
    get_current_datetime,
    setup_date_interval_for_shift_scheduling,
    setup_workers_for_shift_scheduling,
    setup_shifts_for_shift_scheduling,
    initialize_ortools,
]
