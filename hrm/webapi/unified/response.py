"""共用回傳物件"""

from typing import TypeVar, Generic
from pydantic.generics import GenericModel

# 定義泛型 T
T = TypeVar("T")


class WebAPIResponse(GenericModel, Generic[T]):
    """泛型 Response"""
    data: T
    message: str
