from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.schemas.invoices import (
    BankCheckExchange,
    BankCheckOut,
    InvoiceCreate,
    InvoiceDetailOut,
    InvoiceOut,
    PaymentCreate,
    PaymentMethodOut,
    PaymentOut,
)
from app.core.responses import success_response
from app.services.invoices import (
    BankChecksService,
    InvoicesService,
    PaymentsService,
)

invoice_router = APIRouter()


@invoice_router.post("/")
async def create_invoice(
    invoice_in: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = InvoicesService(db)
    data = await service.create(invoice_in)
    return success_response(data=data)


@invoice_router.get("/", response_model=list[InvoiceOut])
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = InvoicesService(db)
    return await service.list()


@invoice_router.get("/payment-methods", response_model=list[PaymentMethodOut])
async def list_payment_methods(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PaymentsService(db)
    return await service.list_methods()


@invoice_router.post("/payments/")
async def register_payment(
    payment_in: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PaymentsService(db)
    data = await service.create(payment_in)
    return success_response(data=data)


@invoice_router.post("/bank-checks/{check_id}/exchange")
async def exchange_bank_check(
    check_id: int,
    exchange_in: BankCheckExchange,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = BankChecksService(db)
    data = await service.mark_as_exchanged(check_id, exchange_in)
    return success_response(data=data)


@invoice_router.get("/payments/{invoice_id}/total")
async def total_paid(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PaymentsService(db)
    return {"total": await service.total_by_invoice(invoice_id)}


@invoice_router.get("/payments/{invoice_id}", response_model=List[PaymentOut])
async def list_payments(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PaymentsService(db)
    return await service.list_by_invoice(invoice_id)


@invoice_router.get("/{invoice_id}/detail", response_model=InvoiceDetailOut)
async def get_invoice_detail(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = InvoicesService(db)
    return await service.detail(invoice_id)


@invoice_router.get("/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = InvoicesService(db)
    return await service.get(invoice_id)
