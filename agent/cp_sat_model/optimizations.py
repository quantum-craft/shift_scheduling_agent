from agent.cp_sat_model.group_solver import GroupSolver


def day_off_request_per_group_optim_loss(
    workers: list[str],
    workers_dict: dict,
    all_shifts: list,
    dates_indices_map: dict,
    group_solver: GroupSolver,
):
    """將每個 group 中每個員工的預排休請求加入最佳化目標中."""

    workers_in_group = group_solver["workers_in_group"]
    shift_schedule = group_solver["shift_schedule"]

    loss = 0
    for w, worker_idx in enumerate(workers_in_group):
        worker_info = workers_dict[workers[worker_idx]]
        for day_off_request in worker_info.get("day_off_requests", []):
            day_off_str = day_off_request.isoformat()
            if day_off_str not in dates_indices_map:
                continue
                # raise ValueError(
                #     f"Day off request {day_off_str} for worker {workers[worker_idx]} not found in dates_indices_map."
                # )

            d = dates_indices_map[day_off_str]

            loss += sum(shift_schedule[(w, d, s)] for s in all_shifts)

    return loss


def work_days_per_group_optim_loss(
    all_days: range,
    all_shifts: range,
    group_solver: GroupSolver,
):
    shift_schedule = group_solver["shift_schedule"]
    workers_in_group = group_solver["workers_in_group"]
    num_workers = len(workers_in_group)
    max_days = len(all_days)
    model = group_solver["model"]

    work_days_list = []
    for w, _ in enumerate(workers_in_group):
        work_days_list.append(
            sum(shift_schedule[(w, d, s)] for d in all_days for s in all_shifts)
        )

    total_work_days = sum(work_days_list)

    # abs_dev = []
    # for days in work_days_list:
    #     a = model.new_int_var(
    #         0, max_days * num_workers, f"abs_work_days_minus_mean_{w}"
    #     )
    #     model.add_abs_equality(a, (days * num_workers) - total_work_days)
    #     abs_dev.append(a)

    # abs_dev_sum = sum(abs_dev)

    return total_work_days  # + abs_dev_sum
