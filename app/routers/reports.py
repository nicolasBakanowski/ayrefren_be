from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.core.responses import success_response
from app.schemas.response import ResponseSchema
from app.services.reports import ReportsService

reports_router = APIRouter()


@reports_router.get("/profit-by-order", response_model=ResponseSchema)
async def report_profit_by_order(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = ReportsService(db)
    data = await service.profit_by_order()
    return success_response(data=data)


@reports_router.get("/billing-by-client", response_model=ResponseSchema)
async def report_billing_by_client(
    start_date: str | None = None,
    end_date: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = ReportsService(db)
    data = await service.billing_by_client(start_date, end_date)
    return success_response(data=data)


@reports_router.get("/top-clients", response_model=ResponseSchema)
async def report_top_clients(db: AsyncSession = Depends(get_db), limit: int = 5):
    service = ReportsService(db)
    data = await service.top_clients(limit=limit)
    return success_response(data=data)


@reports_router.get("/income-monthly", response_model=ResponseSchema)
async def report_income_monthly(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = ReportsService(db)
    data = await service.income_monthly()
    return success_response(data=data)


@reports_router.get("/payments-by-method", response_model=ResponseSchema)
async def report_payments_by_method(
    start_date: str | None = None,
    end_date: str | None = None,
    client_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = ReportsService(db)
    data = await service.payments_by_method(start_date, end_date, client_id)
    return success_response(data=data)


@reports_router.get("/expenses-monthly", response_model=ResponseSchema)
async def report_expenses_monthly(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = ReportsService(db)
    data = await service.expenses_monthly()
    return success_response(data=data)


@reports_router.get("/expenses-by-type", response_model=ResponseSchema)
async def report_expenses_by_type(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = ReportsService(db)
    data = await service.expenses_by_type()
    return success_response(data=data)


@reports_router.get("/monthly-balance", response_model=ResponseSchema)
async def report_monthly_balance(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = ReportsService(db)
    data = await service.monthly_balance()
    return success_response(data=data)


@reports_router.get("/dashboard", response_model=ResponseSchema)
async def report_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = ReportsService(db)
    return success_response(
        data={
            "balance": await service.monthly_balance(),
            "top_clients": await service.top_clients(limit=5),
            "income": await service.income_monthly(),
            "expenses": await service.expenses_monthly(),
        }
    )
