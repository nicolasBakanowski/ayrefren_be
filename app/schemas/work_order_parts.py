from pydantic import BaseModel


class WorkOrderPartBase(BaseModel):
    work_order_id: int
    part_id: int
    quantity: int
    unit_price: float
    subtotal: float


class WorkOrderPartCreate(WorkOrderPartBase):
    pass


class WorkOrderPartOut(WorkOrderPartBase):
    id: int

    class Config:
        from_attributes = True
