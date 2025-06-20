import json
import copy
from pathlib import Path
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from typing import Annotated
from datetime import datetime
from datetime import time
from datetime import date
from datetime import timedelta
from tabulate import tabulate
from agent.cp_sat_model.solver_manager import SolverManager
from agent.cp_sat_model.group_solver import GroupSolver
from ortools.sat.python import cp_model
from models.worker import Worker, Group, PaymentType, EmploymentType
from models.shift import Shift


# TODO: handle multiple solver_manager instances and their life cycles for concurrent requests
solver_manager = SolverManager()


def time_str_to_time(time_str: str, side: str) -> time:
    split = time_str.split(":")
    hour = split[0]
    minute = split[1]

    time_var = time(int(hour), int(minute))

    # if side == "start":
    #     if time_var == time(0, 0):
    #         time_var = time(0, 0, 1)
    # elif side == "end":
    #     if time_var == time(0, 0):
    #         time_var = time(23, 59, 59)
    # else:
    #     raise ValueError(f"Unknown side: {side}")

    return time_var


def convert_start_end(start: time, end: time, bias: timedelta = timedelta(days=0)):
    today = date.today()

    dt_start = datetime.combine(today, start) + bias
    dt_end = datetime.combine(today, end) + bias

    if dt_end <= dt_start:
        dt_end += timedelta(days=1)

    return dt_start, dt_end


def convert_start_end_list(start_ends):
    ret = []
    bias = timedelta(days=0)
    for dt_start, dt_end in start_ends:
        ret.append(convert_start_end(dt_start, dt_end, bias=bias))

        if dt_start > dt_end:
            bias += timedelta(days=1)

    return ret


def check_requirement_length(a: list, b: list, group_name: str):
    if len(a) != len(b):
        return False

    return True


def map_model_status(code: int) -> str:
    if code == cp_model.OPTIMAL:
        # 4
        return "OPTIMAL"
    elif code == cp_model.FEASIBLE:
        # 2
        return "FEASIBLE"
    elif code == cp_model.INFEASIBLE:
        # 3
        return "INFEASIBLE"
    elif code == cp_model.MODEL_INVALID:
        # 1
        return "MODEL_INVALID"
    elif code == cp_model.UNKNOWN:
        # 0
        return "UNKNOWN"
    else:
        raise ValueError(f"Unknown status code: {code}")


def solution_table_rows(
    workers: list[str],
    workers_dict: dict,
    workers_id_to_name: dict[str, str],
    dates: list[date],
    shifts: list,
    work_days: dict,
    group_solver: GroupSolver,
):
    rows = []
    workers_in_group = group_solver["workers_in_group"]
    group_name = group_solver["group_name"].value
    solver = group_solver["solver"]
    shift_schedule = group_solver["shift_schedule"]

    shifts_mark = {}
    for w, _ in enumerate(workers_in_group):
        for d in range(len(dates)):
            shifts_mark[(w, d)] = " "

    for w, worker_idx in enumerate(workers_in_group):
        for d in range(len(dates)):
            for s in range(len(shifts)):
                if solver.value(shift_schedule[(w, d, s)]) == 1:
                    marks = shifts[s].name.split("_")
                    marks = f"{marks[0]}\n{marks[1]}\n-{marks[2]}"
                    shifts_mark[(w, d)] = marks

    for w, worker_idx in enumerate(workers_in_group):
        worker_uuid = workers[worker_idx]

        emp_type = (
            "Full Time"
            if workers_dict[worker_uuid].employment_type == "FT"
            else "Part Time"
        )

        worker_string = f"{workers_id_to_name[worker_uuid]}\n{group_name}\n({emp_type})"

        row = (
            [worker_string]
            + [shifts_mark[(w, d)] for d, _ in enumerate(dates)]
            + [f"{work_days[worker_uuid]} / {len(dates) - work_days[worker_uuid]}"]
        )
        rows.append(row)

    return rows


def calculate_work_days(
    workers: list[str],
    all_days: list[int],
    all_shifts: list[int],
    group_solver: GroupSolver,
):
    solver = group_solver["solver"]
    shift_schedule = group_solver["shift_schedule"]
    workers_in_group = group_solver["workers_in_group"]

    work_days_out = {}
    for w, worker_idx in enumerate(workers_in_group):
        work_days = sum(
            solver.value(shift_schedule[(w, d, s)])
            for d in all_days
            for s in all_shifts
        )

        work_days_out[workers[worker_idx]] = work_days

    return work_days_out


def print_solution(solver_manager: SolverManager):
    headers = (
        ["Employee"]
        + [d.strftime("%d\n%a") for d in solver_manager.dates]
        + ["Work / Off"]
    )
    rows = []
    for group_name, group_solver in solver_manager.group_solvers.items():
        group_name = group_name.value
        group_status = group_solver["solver_status"]
        if group_status == cp_model.OPTIMAL or group_status == cp_model.FEASIBLE:
            print(f"Group {group_name}: {map_model_status(group_status)}")

            work_days = calculate_work_days(
                workers=solver_manager.workers,
                all_days=solver_manager.all_days,
                all_shifts=solver_manager.all_shifts,
                group_solver=group_solver,
            )

            rows.append(
                solution_table_rows(
                    workers=solver_manager.workers,
                    workers_dict=solver_manager.workers_dict,
                    workers_id_to_name=solver_manager.workers_id_to_name,
                    dates=solver_manager.dates,
                    shifts=solver_manager.shifts,
                    work_days=work_days,
                    group_solver=group_solver,
                )
            )

        else:
            print(f"Group {group_name}: {map_model_status(group_status)}")

    rows = [rows[i][j] for i in range(len(rows)) for j in range(len(rows[i]))]

    print(tabulate(rows, headers=headers, tablefmt="grid"))


@tool
def get_current_date() -> datetime:
    """
    取得並回傳當前日期，供後續排程運算使用。

    Returns:
        datetime: 目前的日期。
    """

    return datetime.now().date()


@tool
def setup_date_interval_for_shift_scheduling(
    start_date: Annotated[date, "排班表的起始日期"],
    end_date: Annotated[date, "排班表的結束日期"],
) -> str:
    """
    必須先用工具 get_current_date 取得當前的日期，
    接著根據推斷出的開始與結束日期，設定排班最佳化工具的日期區間。

    Args:
        start_date (date): 排班表的起始日期。
        end_date (date): 排班表的結束日期。

    Returns:
        str: 操作結果訊息，例如 "日期區間設定成功" 或錯誤訊息。
    """

    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)

    all_days = range(len(dates))
    dates_indices_map = {d.isoformat(): i for i, d in enumerate(dates)}

    set_dates_msg = solver_manager.set_dates(
        dates=dates, all_days=all_days, dates_indices_map=dates_indices_map
    )

    return set_dates_msg


@tool
def setup_workers_for_shift_scheduling(config: RunnableConfig) -> str:
    """
    註冊員工清單至排班最佳化工具，以便後續排程使用。

    Returns:
        str: 操作結果訊息，例如 "員工設定成功" 或錯誤訊息。
    """

    # user_dict = config["configurable"]["langgraph_auth_user"]
    # token = user_dict["authorization_header"]
    # print(f"token:{token}")

    # TODO: use token to call api
    with open(Path("local_data/workers_MAY.json"), "r", encoding="utf-8") as f:
        json_dict = json.load(f)

    sorted_items = sorted(json_dict.items(), key=lambda kv: kv[1]["group"])

    # workers_dict 是 dict[員工id, Worker], 用於後面使用員工id查詢員工資料
    workers_dict: dict[str, Worker] = {
        v["id"]: Worker.model_validate(v) for k, v in dict(sorted_items).items()
    }

    # workers 是 list[員工id]
    workers: list[str] = list(workers_dict.keys())
    for i in range(len(workers)):
        workers_dict[workers[i]].workers_idx = i

    # all_workers 是 range(len(workers)), 方便用於後面enumerate
    all_workers = range(len(workers))

    # group_workers 是 dict[Group, list[int]], 用於後面查詢工作群組的員工
    group_workers: dict[Group, list[int]] = {}
    for _, v in workers_dict.items():
        if v.group not in group_workers:
            group_workers[v.group] = []

        group_workers[v.group].append(v.workers_idx)

    # group_workers_idx 是 dict[Group, dict[int, int]], 用於後面反查詢工作群組內員工的順序
    # example: group_workers_idx[Group.出餐_廚房][17] = 0, group_workers_idx[Group.出餐_廚房][20] = 3
    # 員工17號是本群組第0個員工, 員工20號是本群組第3個員工
    group_workers_idx: dict[Group, dict[int, int]] = {}
    for group_name, workers_in_group in group_workers.items():
        group_workers_idx[group_name] = {w: i for i, w in enumerate(workers_in_group)}

    set_workers_msg = solver_manager.set_workers(
        workers=workers,
        all_workers=all_workers,
        workers_dict=workers_dict,
        group_workers=group_workers,
        group_workers_idx=group_workers_idx,
    )

    return set_workers_msg


@tool
def setup_shifts_for_shift_scheduling() -> str:
    """
    註冊班次清單至排班最佳化工具，以便後續排程使用。

    Returns:
        str: 操作結果訊息，例如 "班次設定成功" 或錯誤訊息。
    """

    # user_dict = config["configurable"]["langgraph_auth_user"]
    # token = user_dict["authorization_header"]
    # print(f"token:{token}")

    # TODO: use token to call api
    with open(Path("local_data/shifts_MAY.json"), "r", encoding="utf-8") as f:
        json_dict = json.load(f)

    shifts_json = copy.deepcopy(json_dict)

    # shifts 是 list[班次id, Shift]
    shifts: list[Shift] = [Shift.model_validate(v) for v in shifts_json]

    all_shifts = range(len(shifts))
    shifts_start_ends = [
        (
            shift.shift_start_time,
            shift.shift_end_time,
        )
        for shift in shifts
    ]

    # shifts_idx = {s.id: i for i, s in enumerate(shifts)}

    set_shifts_msg = solver_manager.set_shifts(
        shifts=shifts,
        all_shifts=all_shifts,
        shifts_start_ends=shifts_start_ends,
        # shifts_idx=shifts_idx,
    )

    return set_shifts_msg


@tool
def setup_staff_requirement_for_shift_scheduling() -> str:
    """
    設定內外場最低人數需求至排班最佳化工具，以便後續排程使用。
    此工具一定要在呼叫setup_shifts_for_shift_scheduling(註冊班次清單至排班最佳化工具)之後再呼叫。

    Returns:
         str: 操作結果訊息，例如 "內外場最低人數需求設定成功" 或錯誤訊息。
    """

    if solver_manager.shifts_start_ends is None:
        return "請先設定班別班次(setup_shifts_for_shift_scheduling)，才能設定內外場最低人數需求."

    # user_dict = config["configurable"]["langgraph_auth_user"]
    # token = user_dict["authorization_header"]
    # print(f"token:{token}")

    # TODO: use token to call api
    with open(Path("local_data/staff_requirement.json"), "r", encoding="utf-8") as f:
        staff_requirement = json.load(f)

    # Add more time slots to fit actual MAY schedule, this is a fake data for testing
    staff_requirement["time_slots"].extend(
        [["00:00", "01:00"], ["01:00", "02:00"], ["02:00", "03:00"], ["03:00", "04:00"]]
    )
    for gi in staff_requirement["group_infos"]:
        gi["requirement"].extend([0, 0, 0, 0])

    time_slots = staff_requirement["time_slots"]

    time_slots_start_ends = [
        (time_str_to_time(time_slot[0], "start"), time_str_to_time(time_slot[1], "end"))
        for time_slot in time_slots
    ]

    time_slots_start_ends_converted = convert_start_end_list(time_slots_start_ends)

    covering_shifts = []
    for (
        time_slot_start_converted,
        time_slot_end_converted,
    ) in time_slots_start_ends_converted:

        covering_shift = []
        for shift_idx, (shift_start, shift_end) in enumerate(
            solver_manager.shifts_start_ends
        ):
            shift_start_converted, shift_end_converted = convert_start_end(
                shift_start, shift_end
            )

            if (
                shift_start_converted <= time_slot_start_converted
                and shift_end_converted >= time_slot_end_converted
            ):
                covering_shift.append(shift_idx)

        covering_shifts.append(covering_shift)

    # Error check:
    # Check group requirement length is equal to time_slots length
    for group_info in staff_requirement["group_infos"]:
        a = group_info["requirement"]
        b = covering_shifts
        group_name = group_info["group_name"]

        if (
            check_requirement_length(
                a=a,
                b=b,
                group_name=group_name,
            )
            == False
        ):
            return f"Group {group_name}'s requirement length mismatch: {len(a)} != {len(b)}"

    set_staff_requirement_msg = solver_manager.set_staff_requirement(
        staff_requirement=staff_requirement,
        time_slots=time_slots,
        time_slots_start_ends=time_slots_start_ends,
        covering_shifts=covering_shifts,
    )

    return set_staff_requirement_msg


@tool
def initialize_ortools() -> str:
    """
    初始化排班最佳化工具並回傳狀態結果。

    Returns:
        str: 初始設定結果訊息，例如 "初始化成功" 或錯誤訊息。
    """

    status, _ = solver_manager.init()

    return status


@tool
def add_general_constraints() -> str:
    """
    新增一般性約束條件至排班最佳化工具。

    Returns:
        str: 操作結果訊息，例如 "約束條件設定成功" 或錯誤訊息。
    """

    general_constraints_msg = solver_manager.add_general_constraints()

    return general_constraints_msg


# 最小化工作天數 = 最低成本 ?
@tool
def add_min_work_days_optimization() -> str:
    """
    新增最小化工作天數的最佳化目標至排班最佳化工具。

    Returns:
        str: 操作結果訊息，例如 "最小化工作天數的最佳化目標設定成功" 或錯誤訊息。
    """

    min_work_days_optimization_msg = solver_manager.add_min_work_days_optimization()

    return min_work_days_optimization_msg


# 員工預排休最佳化
@tool
def add_worker_day_off_requests_optimization() -> str:
    """
    新增員工預排休最佳化目標至排班最佳化工具。

    Returns:
        str: 操作結果訊息，例如 "員工預排休的最佳化目標設定成功" 或錯誤訊息。
    """

    with open("local_data/day_off_requests.json", "r", encoding="utf-8") as f:
        day_off_requests = json.load(f)

    worker_day_off_requests_optimization_msg = (
        solver_manager.add_worker_day_off_requests_optimization(
            day_off_requests=day_off_requests
        )
    )

    return worker_day_off_requests_optimization_msg


@tool
def execute_ortools_scheduling_group_solvers() -> str:
    """
    真正執行排班最佳化工具求解器並回傳求解狀態。
    此工具必須在呼叫 initialize_ortools() 並確認初始化成功後才能使用。
    在 initialize_ortools() 和本工具之間，可選擇加入約束(constraints)和最佳化目標(optimization goals)。

    說明：
        此工具會呼叫 solver_manager.solve 方法來啟動排班模型的求解程序。

    回傳值：
        str: solver_manager.solve() 回傳的求解狀態字串，
             表示求解是否成功或失敗，以及相關訊息。
    """

    # Optimizations.
    for group_name, group_loss in solver_manager.group_losses.items():
        solver_manager.group_solvers[group_name]["model"].minimize(group_loss)

    # Solve the model for shift_schedule-s for each group.
    for group_name, group_solver in solver_manager.group_solvers.items():
        group_solver["solver_status"] = group_solver["solver"].solve(
            group_solver["model"]
        )

    return_str = []
    for group_name, group_solver in solver_manager.group_solvers.items():
        group_status = group_solver["solver_status"]
        group_status_str = map_model_status(group_status)

        return_str.append(f"Group {group_name} status: {group_status_str}")

    print_solution(solver_manager)

    return "\n".join(return_str)


shift_scheduling_tool_list = [
    get_current_date,
    setup_date_interval_for_shift_scheduling,
    setup_workers_for_shift_scheduling,
    setup_shifts_for_shift_scheduling,
    setup_staff_requirement_for_shift_scheduling,
    initialize_ortools,
    add_general_constraints,
    add_min_work_days_optimization,
    add_worker_day_off_requests_optimization,
    execute_ortools_scheduling_group_solvers,
]


