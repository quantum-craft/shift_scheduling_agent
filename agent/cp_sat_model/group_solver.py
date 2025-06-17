from typing import TypedDict
from ortools.sat import cp_model_pb2
from ortools.sat.python import cp_model


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
