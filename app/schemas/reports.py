from pydantic import BaseModel


class ProfitReportOut(BaseModel):
    order_id: int
    client_name: str
    invoice_total: float
    parts_cost: float
    labor_cost: float
    profit: float


class MonthlyBalanceOut(BaseModel):
    month: str
    income: float
    expense: float
    balance: float


class ExpenseByTypeOut(BaseModel):
    type: str
    total_amount: float


class ExpenseMonthlyOut(BaseModel):
    month: str
    total_expense: float


class PaymentsByMethodOut(BaseModel):
    method: str
    total_received: float


class IncomeMonthlyOut(BaseModel):
    month: str  # 'YYYY-MM'
    total_income: float


class TopClientOut(BaseModel):
    client_name: str
    total_billed: float


class BillingByClientOut(BaseModel):
    client_id: int
    client_name: str
    total_billed: float
    total_paid: float
