from ortools.sat.python import cp_model
from datetime import datetime
from datetime import date
from datetime import time
from typing import TypedDict
from ortools.sat import cp_model_pb2


class GroupSolver(TypedDict):
    group_name: str
    model: cp_model.CpModel
    solver: cp_model.CpSolver
    solver_status: cp_model_pb2.CpSolverStatus
    shift_schedule: dict
    workers_in_group: list
    workers_in_group_idx: dict
    all_days: range
    all_shifts: range


class SolverManager:
    """Manages OR-Tools solver operations and state."""

    group_solvers: dict[str, GroupSolver] = None

    """Date related data."""
    dates: list[date] = None
    all_days: range = None
    dates_indices_map: dict[str, int] = None

    """Worker(Employee) related data."""
    workers: list[str] = None
    all_workers: range = None
    workers_dict: dict = None
    group_workers: dict = None
    group_workers_idx: dict = None

    """Shift related data."""
    shifts: list[dict] = None
    all_shifts: range = None
    shifts_start_ends: list[time] = None
    shifts_idx: dict[str, int] = None

    def init(self) -> tuple[str, bool]:
        """Initialize the solver and model"""

        (status, status_ok) = self.check_solver_status()
        if not status_ok:
            return status, False

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.linearization_level = 0
        self.solver.parameters.enumerate_all_solutions = (
            False  # Enumerate all solutions. # TODO: performance issue
        )

        self.shift_schedule = {}
        for w in self.all_workers:
            for d in self.all_days:
                for s in self.all_shifts:
                    self.shift_schedule[(w, d, s)] = self.model.new_bool_var(
                        f"shift_w{w}_d{d}_s{s}"
                    )

        return (
            "排班最佳化工具(OR-Tools)的model和solver初始化成功(initialization successful).",
            True,
        )

    def clear(self):
        """Clear current model and solution state"""

        self.shift_schedule = {}
        self.solver = cp_model.CpSolver()
        self.model = cp_model.CpModel()

        # TODO: more and more to be here
        self.clear_shifts()
        self.clear_workers()
        self.clear_dates()
        self.group_solvers = None

    def set_dates(
        self, dates: list[date], all_days: range, dates_indices_map: dict[str, int]
    ) -> str:
        """Set dates, all_days, and dates_indices_map for the scheduling tool(ortools)"""

        try:
            self.dates = dates
            self.all_days = all_days
            self.dates_indices_map = dates_indices_map
        except Exception as e:
            return f"排班最佳化工具的日期區間設定失敗, 錯誤訊息: {e}"

        return "排班最佳化工具的日期區間設定成功."

    def clear_dates(self) -> str:
        """Clear dates, all_days, and dates_indices_map and let the scheduling tool(ortools) understand it need to reset data."""

        try:
            self.dates_indices_map = None
            self.all_days = None
            self.dates = None
        except Exception as e:
            return f"排班最佳化工具的日期區間清除失敗, 錯誤訊息: {e}"

        return "排班最佳化工具的日期區間清除成功."

    def set_workers(
        self,
        workers: list[str],
        all_workers: range,
        workers_dict: dict,
        group_workers: dict,
        group_workers_idx: dict,
    ) -> str:
        """Set workers, all_workers, and workers_dict for the scheduling tool(ortools)"""

        try:
            self.workers = workers
            self.all_workers = all_workers
            self.workers_dict = workers_dict
            self.group_workers = group_workers
            self.group_workers_idx = group_workers_idx
        except Exception as e:
            return f"排班最佳化工具的員工設定失敗, 錯誤訊息: {e}"

        return f"排班最佳化工具的員工設定成功, 此次參與排班人數: {len(self.workers)}"

    def clear_workers(self) -> str:
        """Clear workers, all_workers, and workers_dict and let the scheduling tool(ortools) understand it need to reset data."""

        try:
            self.workers = None
            self.all_workers = None
            self.workers_dict = None
            self.group_workers = None
            self.group_workers_idx = None
        except Exception as e:
            return f"排班最佳化工具的員工清除失敗, 錯誤訊息: {e}"

        return "排班最佳化工具的員工清除成功."

    def set_shifts(
        self,
        shifts: list[dict],
        all_shifts: range,
        shifts_start_ends: list[time],
        shifts_idx: dict[str, int],
    ) -> str:
        """Set shifts, all_shifts, shifts_start_ends, and shifts_idx for the scheduling tool(ortools)"""

        try:
            self.shifts = shifts
            self.all_shifts = all_shifts
            self.shifts_start_ends = shifts_start_ends
            self.shifts_idx = shifts_idx
        except Exception as e:
            return f"排班最佳化工具的班別班次設定失敗, 錯誤訊息: {e}"

        return f"排班最佳化工具的班別班次設定成功, 此次可排班的班別班次: {len(self.shifts)}"

    def clear_shifts(self) -> str:
        """Clear shifts, all_shifts, shifts_start_ends, and shifts_idx and let the scheduling tool(ortools) understand it need to reset data."""

        try:
            self.shifts = None
            self.all_shifts = None
            self.shifts_start_ends = None
            self.shifts_idx = None
        except Exception as e:
            return f"排班最佳化工具的班別班次清除失敗, 錯誤訊息: {e}"

        return "排班最佳化工具的班別班次清除成功."

    def add_general_constraints(self):
        # TODO:
        pass
        # num_workers = len(self.workers)
        # num_shifts = len(self.shifts)

        # # 某一'天'的某一'班次' -> 一定要且只能有一位'員工'上班
        # for d in self.all_days:
        #     for s in range(num_shifts):
        #         self.model.add_exactly_one(
        #             self.shift_schedule[(w, d, s)] for w in range(len(self.workers))
        #         )

        # # 某一'員工'在某一'天' -> 最多能上一個'班次'
        # for w in range(num_workers):
        #     for d in self.all_days:
        #         self.model.add_at_most_one(
        #             self.shift_schedule[(w, d, s)] for s in range(len(self.shifts))
        #         )

        # min_shifts_per_worker = (num_shifts * len(self.all_days)) // num_workers
        # if (num_shifts * len(self.all_days)) % len(self.workers) == 0:
        #     max_shifts_per_worker = min_shifts_per_worker
        # else:
        #     max_shifts_per_worker = min_shifts_per_worker + 1

        # for w in range(num_workers):
        #     shifts_worked = []
        #     for d in self.all_days:
        #         for s in range(num_shifts):
        #             shifts_worked.append(self.shift_schedule[(w, d, s)])

        #     self.model.add(min_shifts_per_worker <= sum(shifts_worked))
        #     self.model.add(sum(shifts_worked) <= max_shifts_per_worker)

    def check_solver_status(self) -> tuple[str, bool]:
        if self.workers is None:
            return (
                "排班最佳化工具(OR-Tools)的員工(Workers)沒有設置, 請詢問使用者更多的資訊.",
                False,
            )

        if self.dates is None:
            return (
                "排班最佳化工具(OR-Tools)的日期區間(Dates)沒有設置, 請詢問使用者更多的資訊.",
                False,
            )

        if self.shifts is None:
            return (
                "排班最佳化工具(OR-Tools)的班次(Shifts)沒有設置, 請詢問使用者更多的資訊.",
                False,
            )

        return (
            "排班最佳化工具(OR-Tools)的資料(Workers, Days, and Shifts)都設置成功",
            True,
        )
