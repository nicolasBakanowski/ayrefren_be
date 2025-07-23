from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.trucks import TruckInDB
from app.schemas.users import UserOut

from .work_order_parts import WorkOrderPartOut
from .work_order_tasks import WorkOrderTaskOut
from .work_orders_mechanic import WorkOrderMechanicOut


class WorkOrderBase(BaseModel):
    truck_id: int
    status_id: int
    reviewed_by: Optional[int] = None
    notes: Optional[str] = None
    fast_phone: Optional[str] = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdate(BaseModel):
    status_id: Optional[int] = None
    notes: Optional[str] = None
    reviewed_by: Optional[int] = None


class WorkOrderStatusOut(BaseModel):
    id: int
    name: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class WorkOrderOut(WorkOrderBase):
    id: int
    created_at: datetime
    truck: Optional[TruckInDB] = None
    status: Optional[WorkOrderStatusOut] = None
    tasks: List[WorkOrderTaskOut] = []
    mechanics: List[WorkOrderMechanicOut] = []
    reviewer: Optional[UserOut] = None
    parts: List[WorkOrderPartOut] = []
    fast_phone: Optional[str] = None

    class Config:
        from_attributes = True


class WorkOrderReviewer(BaseModel):
    work_order_id: int
    reviewer_id: int
