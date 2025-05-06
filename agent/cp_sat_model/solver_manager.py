from ortools.sat.python import cp_model
from datetime import datetime


class SolverManager:
    """Manages OR-Tools solver operations and state"""

    days: list[datetime] = None
    all_days: range = None
    shifts: list[int] = None
    all_shifts: range = None
    workers: list[int] = None
    all_workers: range = None

    def check_solver_status_and_init(self) -> tuple[str, bool]:
        if self.days is None:
            return "Days not set, get more data from the user.", False

        if self.shifts is None:
            return "Shifts not set, get more data from the user.", False

        if self.workers is None:
            return "Workers not set, get more data from the user.", False

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.shift_schedule = {}
        for w in self.all_workers:
            for d in self.all_days:
                for s in self.all_shifts:
                    self.shift_schedule[(w, d, s)] = self.model.new_bool_var(
                        f"shift_w{w}_d{d}_s{s}"
                    )

        return "Solver and model initialized successfully.", True

    def clear(self):
        """Clear current model and solution state"""
        self.shift_schedule = {}

        self.all_days = None
        self.all_shifts = None
        self.all_workers = None

        self.days = None
        self.shifts = None
        self.workers = None

        self.solver = cp_model.CpSolver()
        self.model = cp_model.CpModel()

    def set_days(self, days: list[datetime]):
        """Set the days for the scheduling problem"""

        self.days = days
        self.all_days = range(len(days))

    def set_shifts(self, shifts: list[int]):
        """Set the shifts for the scheduling problem"""

        self.shifts = shifts
        self.all_shifts = range(len(shifts))

    def set_workers(self, workers: list[int]):
        """Set the workers for the scheduling problem"""

        self.workers = workers
        self.all_workers = range(len(workers))
