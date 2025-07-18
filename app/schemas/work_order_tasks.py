from datetime import datetime

from pydantic import BaseModel


class WorkOrderTaskBase(BaseModel):
    work_order_id: int
    user_id: int
    description: str
    area_id: int
    price: float
    external: bool = False


class WorkOrderTaskCreate(WorkOrderTaskBase):
    pass


class WorkOrderTaskOut(WorkOrderTaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
