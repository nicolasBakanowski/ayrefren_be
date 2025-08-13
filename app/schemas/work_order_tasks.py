from datetime import datetime

from pydantic import BaseModel


class WorkOrderTaskBase(BaseModel):
    work_order_id: int
    user_id: int
    description: str
    area_id: int
    price: float
    external: bool = False
    paid: bool = False


class WorkOrderTaskCreate(WorkOrderTaskBase):
    pass


class WorkOrderTaskUpdate(BaseModel):
    work_order_id: int | None = None
    user_id: int | None = None
    description: str | None = None
    area_id: int | None = None
    price: float | None = None
    external: bool | None = None
    paid: bool | None = None


class WorkOrderTaskOut(WorkOrderTaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
