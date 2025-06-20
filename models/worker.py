from enum import Enum
from datetime import date
from pydantic import BaseModel, Field, ConfigDict


class PaymentType(str, Enum):
    MONTHLY = "monthly"
    HOURLY = "hourly"


class EmploymentType(str, Enum):
    FT = "FT"
    PT = "PT"


class Group(str, Enum):
    主管 = "0_主管"
    廚房 = "1_廚房"
    切肉區 = "2_切肉區"
    出餐 = "3_出餐"
    出餐_廚房 = "4_出餐_廚房"
    洗滌 = "5_洗滌"


class Worker(BaseModel):
    name: str = Field(description="員工姓名")
    id: str = Field(description="員工ID")
    pay: int = Field(description="員工薪資")
    payment_type: PaymentType = Field(description="員工薪資類型")
    employment_type: EmploymentType = Field(description="員工雇用類型")
    group: Group = Field(description="員工工作群組")
    workers_idx: int = Field(description="員工在員工列表中的索引", default=-1)
    day_off_requests: list[date] = Field(description="員工預排休日期", default=[])
