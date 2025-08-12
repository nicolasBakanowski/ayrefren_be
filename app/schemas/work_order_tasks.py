from datetime import datetime

from pydantic import BaseModel, Field


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
    paid_at: datetime | None = None

    class Config:
        from_attributes = True


class ByUserSummary(BaseModel):
    user_id: int
    total_amount: float
    count: int


class TasksSummaryOut(BaseModel):
    total_amount: float
    count: int
    by_user: list[ByUserSummary] = []


class TasksFilterOut(BaseModel):
    area_id: int = 1
    from_: datetime | None = Field(None, alias="from")
    to: datetime | None = None
    paid: bool | None = False
    only_finalized: bool = True
    external: bool = False

    class Config:
        populate_by_name = True

class TasksResponse(BaseModel):
    items: list[WorkOrderTaskOut]
    summary: TasksSummaryOut
    filters: TasksFilterOut


class MarkPaidIn(BaseModel):
    task_ids: list[int]
    paid: bool = True
    paid_at: datetime | None = None


class MarkPaidOut(BaseModel):
    updated: int
