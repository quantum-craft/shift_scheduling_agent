from langchain_core.tools import tool
from typing import Annotated
from datetime import datetime
from datetime import timedelta
from pydantic import BaseModel, Field
from agent.cp_sat_model.solver_manager import SolverManager


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
def get_datetime_table(
    start_date_time: Annotated[datetime, "班表開始的日期."],
    end_date_time: Annotated[datetime, "班表結束的日期."],
) -> list[datetime]:
    """
    在知道班表的開始和結束日期後, 獲取其間所有的日期和時間.

    returns:
        list[datetime]: 其間所有的日期和時間.
    """

    ret_days = []
    current = start_date_time
    while current <= end_date_time:
        ret_days.append(current)
        current += timedelta(days=1)

    solver_manager.set_days(ret_days)
    solver_manager.set_workers([1, 2, 3, 4])
    solver_manager.set_shifts([1, 2, 3, 4])
    status, init_ok = solver_manager.check_solver_status_and_init()
    print(status)

    return ret_days


shift_scheduling_tool_list = [get_current_datetime, get_datetime_table]
