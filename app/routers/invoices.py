from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.schemas.invoices import (
    InvoiceCreate,
    InvoiceDetailOut,
    InvoiceOut,
    PaymentCreate,
    PaymentMethodOut,
    PaymentOut,
)
from app.services.invoices import InvoicesService, PaymentsService

invoice_router = APIRouter()


@invoice_router.post("/", response_model=InvoiceOut)
async def create_invoice(
    invoice_in: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = InvoicesService(db)
    return await service.create(invoice_in)


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


@invoice_router.post("/payments/", response_model=PaymentOut)
async def register_payment(
    payment_in: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PaymentsService(db)
    return await service.create(payment_in)


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
