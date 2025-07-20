from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class ExpenseTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ExpenseCreate(BaseModel):
    date: date
    amount: Decimal
    description: str | None = None
    expense_type_id: int | None


class ExpenseOut(ExpenseCreate):
    id: int
    created_at: datetime
    expense_type: ExpenseTypeOut | None = None

    class Config:
        from_attributes = True
