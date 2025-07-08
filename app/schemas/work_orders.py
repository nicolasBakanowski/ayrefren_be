from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WorkOrderBase(BaseModel):
    client_id: int
    truck_id: int
    status_id: int
    notes: Optional[str] = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdate(BaseModel):
    status_id: Optional[int]
    notes: Optional[str]


from app.schemas.clients import ClientOut
from app.schemas.trucks import TruckInDB
from app.schemas.users import UserOut


class WorkOrderStatusOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class WorkOrderOut(WorkOrderBase):
    id: int
    created_at: datetime
    truck: TruckInDB
    client: ClientOut
    status: WorkOrderStatusOut
    reviewer: Optional[UserOut] = None

    class Config:
        from_attributes = True
