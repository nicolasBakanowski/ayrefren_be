from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.invoices import BankCheckType

from .clients import ClientOut


class InvoiceTypeBase(BaseModel):
    name: str

    class Config:
        from_attributes = True


class InvoiceTypeFull(InvoiceTypeBase):
    id: int
    name: str
    surcharge: Optional[float] = None

    class Config:
        from_attributes = True


class InvoiceStatus(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


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


class InvoiceUpdate(BaseModel):
    status_id: Optional[int] = None
    invoice_type_id: Optional[int] = None


class InvoiceOut(InvoiceCreate):
    id: int
    issued_at: datetime
    paid: float
    accepted: bool
    client: ClientOut
    status: InvoiceStatus
    invoice_type: InvoiceTypeFull
    payments: list["PaymentOut"] | None = None

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    invoice_id: int
    method_id: int
    amount: float
    reference: Optional[str] = None
    notes: Optional[str] = None
    bank_checks: Optional[list["BankCheckIn"]] = None


class BankCheckIn(BaseModel):
    bank_name: str
    check_number: str
    amount: float
    type: BankCheckType
    due_date: Optional[datetime] = None


class BankCheckOut(BankCheckIn):
    id: int
    issued_at: datetime
    exchange_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentMethodOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class BankCheckExchange(BaseModel):
    exchange_date: datetime


class InvoiceDetailOut(InvoiceOut):
    surcharge: float
    total_without_surcharge: float
    total_with_surcharge: float


class PaymentOut(PaymentCreate):
    id: int
    date: datetime
    bank_checks: list[BankCheckOut] | None
    method: PaymentMethodOut

    class Config:
        from_attributes = True
