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
    獲取當前的日期和時間.

    returns:
        datetime: 當前的日期和時間.
    """

    return datetime.now()


@tool
def setup_date_interval_for_shift_scheduling(
    start_date_time: Annotated[datetime, "班表開始的日期時間"],
    end_date_time: Annotated[datetime, "班表結束的日期時間"],
) -> str:
    """
    說明：
        必須先用工具 get_current_datetime() 取得當前的日期和時間，
        接著據此推算出排班表的起始與結束日期。

    功能：
        根據 start_date_time 與 end_date_time, 自動產生這段期間內每一天的時間區間,
        設定好排班工具後可用於後續排班設定。

    參數：
        start_date_time (datetime)：排班表的起始日期與時間。
        end_date_time (datetime)：排班表的結束日期與時間。

    回傳值：
        str: 設定結果狀態。若成功，回傳 "設定成功";若失敗，回傳錯誤訊息。
    """

    ret_days = []
    current = start_date_time
    while current <= end_date_time:
        ret_days.append(current)
        current += timedelta(days=1)

    solver_manager.set_days(ret_days)

    # TODO: refactor mock workers and shifts
    solver_manager.set_workers(
        [
            Worker(worker_id="張三"),
            Worker(worker_id="李四"),
            Worker(worker_id="王五"),
            Worker(worker_id="趙六"),
        ]
    )
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

    status, init_ok = solver_manager.init()

    return "排班工具的日期區間設定成功."


shift_scheduling_tool_list = [
    get_current_datetime,
    setup_date_interval_for_shift_scheduling,
]
