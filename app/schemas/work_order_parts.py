from pydantic import BaseModel


class WorkOrderPartBase(BaseModel):
    work_order_id: int
    name: str
    quantity: int
    unit_price: float
    subtotal: float
    increment_per_unit: float = 1.0  # Default increment per unit


class WorkOrderPartCreate(WorkOrderPartBase):
    pass


class WorkOrderPartOut(WorkOrderPartBase):
    id: int

    class Config:
        from_attributes = True
