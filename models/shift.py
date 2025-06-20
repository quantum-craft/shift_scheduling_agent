from enum import Enum
from datetime import date, time
from pydantic import BaseModel, Field, ConfigDict
from models.worker import EmploymentType


class Shift(BaseModel):
    name: str
    id: str
    employment_type: EmploymentType = Field(description="員工雇用類型")  # optional
    shift_start_time: time = Field(description="班表開始時間")
    shift_end_time: time = Field(description="班表結束時間")
    rest_start_time: time | None = Field(description="休息開始時間")
    rest_end_time: time | None = Field(description="休息結束時間")
