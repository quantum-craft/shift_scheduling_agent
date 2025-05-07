from ortools.sat.python import cp_model
from datetime import datetime
from agent.cp_sat_model.shift import Shift
from agent.cp_sat_model.worker import Worker


class SolverManager:
    """Manages OR-Tools solver operations and state"""

    days: list[datetime] = None
    shifts: list[Shift] = None
    workers: list[Worker] = None

    def check_solver_status(self) -> tuple[str, bool]:
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

        if self.workers is None:
            return (
                "排班最佳化工具(OR-Tools)的員工(Workers)沒有設置, 請詢問使用者更多的資訊.",
                False,
            )

        return (
            "排班最佳化工具(OR-Tools)的資料(Days, Shifts, and Workers)都設置成功",
            True,
        )

    def init(self) -> tuple[str, bool]:
        """Initialize the solver and model"""

        (status, status_ok) = self.check_solver_status()

        if not status_ok:
            return status, False

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.shift_schedule = {}
        for w in range(len(self.workers)):
            for d in range(len(self.days)):
                for s in range(len(self.shifts)):
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

        self.days = None
        self.shifts = None
        self.workers = None

        self.solver = cp_model.CpSolver()
        self.model = cp_model.CpModel()

    def set_days(self, days: list[datetime]):
        """Set the days for the scheduling tool"""
        self.days = days

    def set_shifts(self, shifts: list[Shift]):
        """Set the shifts for the scheduling tool"""
        self.shifts = shifts

    def set_workers(self, workers: list[Worker]):
        """Set the workers for the scheduling tool"""
        self.workers = workers
