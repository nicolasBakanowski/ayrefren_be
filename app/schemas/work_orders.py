from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WorkOrderBase(BaseModel):
    truck_id: int
    status_id: int
    notes: Optional[str] = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdate(BaseModel):
    status_id: Optional[int]
    notes: Optional[str]


class WorkOrderOut(WorkOrderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
