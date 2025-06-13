from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from typing import Annotated
from datetime import datetime
from datetime import time
from datetime import timedelta
from pydantic import BaseModel, Field
from agent.cp_sat_model.solver_manager import SolverManager
from agent.cp_sat_model.worker import Worker
from agent.cp_sat_model.shift import Shift
from ortools.sat.python import cp_model
from agent.cp_sat_model.solution_output import WorkersPartialSolutionPrinter

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
    end_date_time: Annotated[datetime, "排班表的結束日期時間"]
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
def setup_workers_for_shift_scheduling(config: RunnableConfig) -> str:
    """
    註冊員工清單至排班最佳化工具，以便後續排程使用。

    Returns:
        str: 操作結果訊息，例如 "員工設定成功" 或錯誤訊息。
    """

    user_dict = config["configurable"]["langgraph_auth_user"]
    token = user_dict["authorization_header"]
    # TODO use token to call api
    print(f"token:{token}")

    solver_manager.set_workers(
        [
            Worker(worker_name="張三"),
            Worker(worker_name="李四"),
            Worker(worker_name="王五"),
            Worker(worker_name="趙六"),
            Worker(worker_name="甲"),
            Worker(worker_name="乙"),
            Worker(worker_name="丙"),
            Worker(worker_name="丁"),
            Worker(worker_name="戊"),
            Worker(worker_name="己"),
            Worker(worker_name="庚"),
            Worker(worker_name="辛"),
            Worker(worker_name="壬"),
            Worker(worker_name="癸"),
            Worker(worker_name="子午未"),
        ]
    )

    return "排班最佳化工具的員工設定成功."


@tool
def setup_department_for_shift_scheduling(
    department: Annotated[str, "部門名稱"],
    department_id: Annotated[str, "部門ID"],
) -> str:
    """
    設定部門資訊，供排班最佳化工具使用。

    Args:
        department (str): 部門名稱。
        department_id (str): 部門ID。

    Returns:
        str: 操作結果訊息，例如 "部門設定成功" 或錯誤訊息。
    """

    solver_manager.set_department(department, department_id)

    return "排班最佳化工具的部門設定成功."


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
            Shift(
                id="夜班",
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


@tool
def add_general_constraints() -> str:
    """
    新增一般性約束條件至排班最佳化工具。

    Returns:
        str: 操作結果訊息，例如 "約束條件設定成功" 或錯誤訊息。
    """

    solver_manager.add_general_constraints()

    return "排班最佳化工具的一般性約束條件設定成功."


@tool
def add_leave_requirement_constraints(
    leave_people: Annotated[list[Worker], "請假人員清單"],
    leave_days: Annotated[list[datetime], "請假日期清單"],
) -> str:
    """
    新增區間內請假人員與日期的約束條件至排班最佳化工具。

    Args:
        leave_people (list[Worker]): 請假人員清單。
        leave_days (list[datetime]): 請假日期清單。

    Returns:
        str: 操作結果訊息，例如 "新增區間內請假人員與日期的約束條件設定成功" 或錯誤訊息。
    """

    solver_manager.add_leave_requirement_constraints(
        leave_people=leave_people, leave_days=leave_days
    )

    return "排班最佳化工具的區間內請假人員與日期設定成功."


@tool
def add_post_requirement_constraints() -> str:
    """
    新增區間內崗位人員最低需求至排班最佳化工具。

    Returns:
        str: 操作結果訊息，例如 "新增區間內崗位人員最低需求設定成功" 或錯誤訊息。
    """

    # TODO:
    pass


@tool
def execute_ortools_scheduling_solver() -> str:
    """
    真正執行排班最佳化工具求解器並回傳求解狀態。
    此工具必須在呼叫 initialize_ortools() 並確認初始化成功後才能使用。
    在 initialize_ortools() 和本工具之間，可選擇加入約束(constraints)和最佳化目標(optimization goals)。
    額外constraints和optimization goals非必須。

    說明：
        此工具會呼叫 solver_manager.solve 方法來啟動排班模型的求解程序。

    回傳值：
        str: solver_manager.solve() 回傳的求解狀態字串，
             表示求解是否成功或失敗，以及相關訊息。
    """

    # Display the first five solutions.
    solution_printer = WorkersPartialSolutionPrinter(
        solver_manager.shift_schedule,
        len(solver_manager.workers),
        len(solver_manager.days),
        len(solver_manager.shifts),
        solution_limit=5,
    )

    status = solver_manager.solver.solve(
        solver_manager.model, solution_callback=solution_printer
    )

    print(
        "workers: ",
        len(solver_manager.workers),
        "days: ",
        len(solver_manager.days),
        "shifts: ",
        len(solver_manager.shifts),
    )

    if status == cp_model.OPTIMAL:
        return "OPTIMAL"
    elif status == cp_model.FEASIBLE:
        return "FEASIBLE"
    elif status == cp_model.INFEASIBLE:
        return "INFEASIBLE"
    else:
        return status


shift_scheduling_tool_list = [
    get_current_datetime,
    setup_date_interval_for_shift_scheduling,
    setup_workers_for_shift_scheduling,
    setup_shifts_for_shift_scheduling,
    initialize_ortools,
    add_general_constraints,
    execute_ortools_scheduling_solver,
]
