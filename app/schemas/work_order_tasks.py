from datetime import date, datetime
from typing import List, Optional

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
    paid: bool
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkOrderTasksSummaryOut(BaseModel):
    work_area_id: int
    date_from: date
    date_to: date
    paid: bool
    count: int
    total_amount: float
    tasks: List[WorkOrderTaskOut]


class WorkOrderTaskMarkPaid(BaseModel):
    task_ids: List[int]
    paid_at: Optional[datetime] = None
