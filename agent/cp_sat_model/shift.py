from datetime import time


class Shift:
    def __init__(self, id: str, start_time: time, end_time: time):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
