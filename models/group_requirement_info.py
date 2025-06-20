from pydantic import BaseModel, Field
from models.worker import Group


class GroupRequirementInfo(BaseModel):
    group_id: Group = Field(description="群組ID")
    group_name: str = Field(description="群組名稱", default="")  # optional
    requirement: list[int] = Field(description="群組需求, 對應TimeSlot的數量")
