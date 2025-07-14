from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.trucks import TruckInDB
from app.schemas.users import UserOut


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
    truck: Optional[TruckInDB] = None
    status: Optional["WorkOrderStatusOut"] = None
    reviewer: Optional[UserOut] = None

    class Config:
        from_attributes = True


class WorkOrderStatusOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
