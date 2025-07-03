from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InvoiceCreate(BaseModel):
    work_order_id: int
    client_id: int
    invoice_type_id: int
    status_id: int
    labor_total: float
    parts_total: float
    iva: float
    total: float
    invoice_number: Optional[str] = None


class InvoiceOut(InvoiceCreate):
    id: int
    issued_at: datetime
    paid: float

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    invoice_id: int
    method_id: int
    amount: float
    reference: Optional[str] = None
    notes: Optional[str] = None


class PaymentOut(PaymentCreate):
    id: int
    date: datetime

    class Config:
        from_attributes = True
