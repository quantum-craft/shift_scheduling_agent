from ortools.sat.python import cp_model
from agent.cp_sat_model.group_solver import GroupSolver
from models.group_requirement_info import GroupRequirementInfo


def one_day_one_shift_constraint(
    all_days: range,
    all_shifts: range,
    group_solvers: dict[str, GroupSolver],
):
    # 某一員工在某一天最多只能上一個班次.

    for _, group_solver in group_solvers.items():
        for w in range(len(group_solver["workers_in_group"])):
            for d in all_days:
                group_solver["model"].add_at_most_one(
                    group_solver["shift_schedule"][(w, d, s)] for s in all_shifts
                )


def worker_shift_constraint(
    workers: list[str],
    workers_dict: dict,
    all_days: range,
    all_shifts: range,
    shifts: list[dict],
    group_solvers: dict[str, GroupSolver],
):
    # FullTime的人員只能拿FT的班次, PartTime的人員只能拿PT班次.

    for _, group_solver in group_solvers.items():
        for w, worker_idx in enumerate(group_solver["workers_in_group"]):
            emp_type = workers_dict[workers[worker_idx]].employment_type
            if emp_type == "FT":
                for d in all_days:
                    for s in all_shifts:
                        if shifts[s].employment_type != "FT":
                            group_solver["model"].add(
                                group_solver["shift_schedule"][(w, d, s)] == 0
                            )
            elif emp_type == "PT":
                for d in all_days:
                    for s in all_shifts:
                        if shifts[s].employment_type != "PT":
                            group_solver["model"].add(
                                group_solver["shift_schedule"][(w, d, s)] == 0
                            )
            else:
                raise ValueError(f"Unknown employment type: {emp_type}")


def staff_requirement_constraint(
    all_days: range,
    group_requirement_infos: list[GroupRequirementInfo],
    covering_shifts: list[list[int]],
    group_solvers: dict[str, GroupSolver],
):
    # 內場最低人數需求

    for group_info in group_requirement_infos:
        group_id = group_info.group_id
        for slot_idx, slot_requirement in enumerate(group_info.requirement):
            if slot_requirement > 0:
                if len(covering_shifts[slot_idx]) == 0:
                    raise ValueError(
                        f"covering_shifts for slot_idx {slot_idx} is empty in group {group_id}"
                    )

                for d in all_days:
                    group_solver = group_solvers[group_id]
                    group_solver["model"].add(
                        sum(
                            group_solver["shift_schedule"][(w, d, s)]
                            for w in range(len(group_solver["workers_in_group"]))
                            for s in covering_shifts[slot_idx]
                        )
                        >= slot_requirement
                    )


def labor_law_days_off_constraint(
    all_days: range, all_shifts: range, group_solvers: dict[str, GroupSolver]
):
    # 勞基法
    # 四週變形工時
    # 勞工每2週內至少應有2日之例假
    # 勞工每4週內之例假及休息日至少應有8日

    group_days_off = {
        "0_主管": {"days_off_14": 0, "days_off_28": 0},
        "1_廚房": {"days_off_14": 2, "days_off_28": 8},
        "2_切肉區": {"days_off_14": 2, "days_off_28": 8},
        "3_出餐": {
            "days_off_14": 0,
            "days_off_28": 0,
        },
        "4_出餐_廚房": {
            "days_off_14": 2,
            "days_off_28": 8,
        },
        "5_洗滌": {"days_off_14": 2, "days_off_28": 8},
    }

    for group_name, days_off in group_days_off.items():
        sliding_window_days_off_constraint(
            window_size=14,
            days_off=days_off["days_off_14"],
            group_name=group_name,
            all_days=all_days,
            all_shifts=all_shifts,
            group_solvers=group_solvers,
        )

    for group_name, days_off in group_days_off.items():
        sliding_window_days_off_constraint(
            window_size=28,
            days_off=days_off["days_off_28"],
            group_name=group_name,
            all_days=all_days,
            all_shifts=all_shifts,
            group_solvers=group_solvers,
        )


# Regular day off => "例假日"
# Rest day => "休息日"
def sliding_window_days_off_constraint(
    window_size: int,
    days_off: int,
    group_name: str,
    all_days: range,
    all_shifts: range,
    group_solvers: dict[str, GroupSolver],
):
    group_solver = group_solvers[group_name]

    for w in range(len(group_solver["workers_in_group"])):
        for d in range(all_days.start, all_days.stop - window_size + 1):
            group_solver["model"].add(
                sum(
                    group_solver["shift_schedule"][(w, d, s)]
                    for d in range(d, d + window_size)
                    for s in all_shifts
                )
                <= window_size - days_off
            )
