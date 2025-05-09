from ortools.sat.python import cp_model
from datetime import datetime
from agent.cp_sat_model.shift import Shift
from agent.cp_sat_model.worker import Worker


class SolverManager:
    """Manages OR-Tools solver operations and state"""

    workers: list[Worker] = None
    days: list[datetime] = None
    shifts: list[Shift] = None

    def init(self) -> tuple[str, bool]:
        """Initialize the solver and model"""

        (status, status_ok) = self.check_solver_status()
        if not status_ok:
            return status, False

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.linearization_level = 0
        self.solver.parameters.enumerate_all_solutions = (
            True  # Enumerate all solutions.
        )

        num_workers = len(self.workers)
        num_days = len(self.days)
        num_shifts = len(self.shifts)

        self.shift_schedule = {}
        for w in range(num_workers):
            for d in range(num_days):
                for s in range(num_shifts):
                    self.shift_schedule[(w, d, s)] = self.model.new_bool_var(
                        f"shift_w{w}_d{d}_s{s}"
                    )

        # 某一'天'的某一'班次' -> 一定要且只能有一位'員工'上班
        for d in range(num_days):
            for s in range(num_shifts):
                self.model.add_exactly_one(
                    self.shift_schedule[(w, d, s)] for w in range(len(self.workers))
                )

        # 某一'員工'在某一'天' -> 最多能上一個'班次'
        for w in range(num_workers):
            for d in range(num_days):
                self.model.add_at_most_one(
                    self.shift_schedule[(w, d, s)] for s in range(len(self.shifts))
                )

        min_shifts_per_worker = (num_shifts * num_days) // num_workers
        if (num_shifts * num_days) % len(self.workers) == 0:
            max_shifts_per_worker = min_shifts_per_worker
        else:
            max_shifts_per_worker = min_shifts_per_worker + 1

        for n in range(num_workers):
            shifts_worked = []
            for d in range(num_days):
                for s in range(num_shifts):
                    shifts_worked.append(self.shift_schedule[(w, d, s)])

            self.model.add(min_shifts_per_worker <= sum(shifts_worked))
            self.model.add(sum(shifts_worked) <= max_shifts_per_worker)

        return (
            "排班最佳化工具(OR-Tools)的model和solver初始化成功(initialization successful).",
            True,
        )

    def clear(self):
        """Clear current model and solution state"""

        self.shifts = None
        self.days = None
        self.workers = None

        self.shift_schedule = {}
        self.solver = cp_model.CpSolver()
        self.model = cp_model.CpModel()

    def set_workers(self, workers: list[Worker]):
        """Set the workers for the scheduling tool"""
        self.workers = workers

    def set_days(self, days: list[datetime]):
        """Set the days for the scheduling tool"""
        self.days = days

    def set_shifts(self, shifts: list[Shift]):
        """Set the shifts for the scheduling tool"""
        self.shifts = shifts

    def check_solver_status(self) -> tuple[str, bool]:
        if self.workers is None:
            return (
                "排班最佳化工具(OR-Tools)的員工(Workers)沒有設置, 請詢問使用者更多的資訊.",
                False,
            )

        if self.days is None:
            return (
                "排班最佳化工具(OR-Tools)的日期區間(Days)沒有設置, 請詢問使用者更多的資訊.",
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
