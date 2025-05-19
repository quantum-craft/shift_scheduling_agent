class Worker:
    def __init__(
        self,
        worker_name: str,
        worker_id: str = "ABCDEFG",
        pay: int = 0,
        pay_type: str = "hourly",
    ):
        self.worker_name = worker_name
        self.worker_id = worker_id
        self.pay = pay
        self.pay_type = pay_type
