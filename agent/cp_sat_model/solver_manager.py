from ortools.sat.python import cp_model
from datetime import datetime
from datetime import date
from datetime import time
from agent.cp_sat_model.constraints import worker_shift_constraint
from agent.cp_sat_model.constraints import one_day_one_shift_constraint
from agent.cp_sat_model.constraints import staff_requirement_constraint
from agent.cp_sat_model.group_solver import GroupSolver


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

    """Optimization related data."""
    group_losses: dict = None

    def init(self) -> tuple[str, bool]:
        """Initialize group solvers and models for each group"""

        (status, status_ok) = self.check_solver_status()
        if not status_ok:
            return status, False

        self.group_solvers = {}
        for group_name, workers_in_group in self.group_workers.items():
            model = cp_model.CpModel()
            model.name = f"model_{group_name}"

            solver = cp_model.CpSolver()
            # 這個參數對performance的影響是什麼?
            solver.parameters.linearization_level = 0
            solver.parameters.enumerate_all_solutions = False
            # solver.parameters.max_deterministic_time = 5
            # solver.parameters.max_time_in_seconds = 5

            shift_schedule = {}
            for w in range(len(workers_in_group)):
                for d in self.all_days:
                    for s in self.all_shifts:
                        shift_schedule[(w, d, s)] = model.new_bool_var(
                            f"shift_w{w}_d{d}_s{s}"
                        )

            self.group_solvers[group_name] = GroupSolver(
                group_name=group_name,
                model=model,
                solver=solver,
                solver_status=None,
                shift_schedule=shift_schedule,
                workers_in_group=workers_in_group,
                workers_in_group_idx=self.group_workers_idx[group_name],
                all_days=self.all_days,
                all_shifts=self.all_shifts,
            )

        # Init optimization related data
        self.group_losses = {}
        for group_name, _ in self.group_solvers.items():
            self.group_losses[group_name] = 0

        return (
            "排班最佳化工具的group models, solvers, and optimization losses 初始化成功.",
            True,
        )

    def clear(self):
        """Clear group models and solver states."""

        self.clear_staff_requirement()
        self.clear_shifts()
        self.clear_workers()
        self.clear_dates()
        self.group_losses = None
        self.group_solvers = None

    def check_solver_status(self) -> tuple[str, bool]:
        if self.workers is None:
            return (
                "排班最佳化工具的員工(workers)沒有設置, 此tool一定要在呼叫setup_workers_for_shift_scheduling後呼叫.",
                False,
            )

        if self.dates is None:
            return (
                "排班最佳化工具的日期區間(dates)沒有設置, 此tool一定要在呼叫setup_date_interval_for_shift_scheduling後呼叫.",
                False,
            )

        if self.shifts is None:
            return (
                "排班最佳化工具的班次(shifts)沒有設置, 此tool一定要在呼叫setup_shifts_for_shift_scheduling後呼叫.",
                False,
            )

        if self.group_workers is None:
            return (
                "排班最佳化工具的員工群組(group_workers)沒有設置, 此tool一定要在呼叫setup_workers_for_shift_scheduling後呼叫.",
                False,
            )

        return (
            "排班最佳化工具的資料(workers, days, shifts, and group_workers)都設置成功",
            True,
        )

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

    def set_staff_requirement(
        self,
        staff_requirement: dict,
        time_slots: list[list],
        time_slots_start_ends: list[tuple],
        covering_shifts: list[list],
    ) -> str:
        """Set staff_requirement, time_slots, time_slots_start_ends, and covering_shifts for the scheduling tool(ortools)"""

        try:
            self.staff_requirement = staff_requirement
            self.time_slots = time_slots
            self.time_slots_start_ends = time_slots_start_ends
            self.covering_shifts = covering_shifts
        except Exception as e:
            return f"排班最佳化工具的內外場最低人數需求設定失敗, 錯誤訊息: {e}"

        return "排班最佳化工具的內外場最低人數需求設定成功."

    def clear_staff_requirement(self) -> str:
        """Clear staff_requirement, time_slots, time_slots_start_ends, and covering_shifts and let the scheduling tool(ortools) understand it need to reset data."""

        try:
            self.staff_requirement = None
            self.time_slots = None
            self.time_slots_start_ends = None
            self.covering_shifts = None
        except Exception as e:
            return f"排班最佳化工具的內外場最低人數需求清除失敗, 錯誤訊息: {e}"

        return "排班最佳化工具的內外場最低人數需求清除成功."

    def add_general_constraints(self) -> str:
        try:
            # FullTime的人員只能拿FT的班次, PartTime的人員只能拿PT班次.
            worker_shift_constraint(
                workers=self.workers,
                workers_dict=self.workers_dict,
                all_days=self.all_days,
                all_shifts=self.all_shifts,
                shifts=self.shifts,
                group_solvers=self.group_solvers,
            )

            # 某一員工在某一天最多只能上一個班次.
            one_day_one_shift_constraint(
                all_days=self.all_days,
                all_shifts=self.all_shifts,
                group_solvers=self.group_solvers,
            )

            # 符合內場最低人數需求
            staff_requirement_constraint(
                all_days=self.all_days,
                staff_requirement=self.staff_requirement,
                covering_shifts=self.covering_shifts,
                group_solvers=self.group_solvers,
            )
        except Exception as e:
            return f"排班最佳化工具的一般性約束條件設定失敗, 錯誤訊息: {e}"

        return "排班最佳化工具的一般性約束條件設定成功."
