from ortools.sat.python import cp_model


class WorkersPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, shifts, num_workers, num_days, num_shifts, solution_limit):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._num_workers = num_workers
        self._num_days = num_days
        self._num_shifts = num_shifts
        self._solution_count = 0
        self._solution_limit = solution_limit

    def on_solution_callback(self):
        self._solution_count += 1
        print(f"Solution {self._solution_count}")

        for d in range(self._num_days):
            print(f"Day {d}")
            for n in range(self._num_workers):
                is_working = False
                for s in range(self._num_shifts):
                    if self.value(self._shifts[(n, d, s)]):
                        is_working = True
                        print(f"  Worker {n} works shift {s}")
                if not is_working:
                    print(f"  Worker {n} does not work")

        if self._solution_count >= self._solution_limit:
            print(f"Stop search after {self._solution_limit} solutions")
            self.stop_search()

    def solutionCount(self):
        return self._solution_count
