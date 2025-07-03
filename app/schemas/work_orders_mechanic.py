from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WorkOrderMechanicBase(BaseModel):
    work_order_id: int
    user_id: int
    area_id: int
    notes: Optional[str] = None


class WorkOrderMechanicCreate(WorkOrderMechanicBase):
    pass


class WorkOrderMechanicOut(WorkOrderMechanicBase):
    id: int
    joined_at: datetime

    class Config:
        from_attributes = True


class WorkAreaOut(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True
