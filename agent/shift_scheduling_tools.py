from langchain_core.tools import tool
from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field


@tool
def get_current_datetime() -> datetime:
    """
    獲取當前的日期和時間。

    returns:
        datetime: 當前的日期和時間。
    """

    return datetime.now()


shift_scheduling_tool_list = [get_current_datetime]
