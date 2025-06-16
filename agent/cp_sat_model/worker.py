from pydantic import BaseModel


class Worker(BaseModel):
    name: str
    id: str
    pay: int
    payment_type: str
    employment_type: str
    group: str
