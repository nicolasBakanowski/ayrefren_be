from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.core.responses import success_response
from app.schemas.invoices import (
    BankCheckExchange,
    BankCheckOut,
    InvoiceCreate,
    InvoiceDetailOut,
    InvoiceOut,
    InvoiceUpdate,
    PaymentCreate,
    PaymentMethodOut,
    PaymentOut,
)
from app.schemas.response import ResponseSchema
from app.services.invoices import BankChecksService, InvoicesService, PaymentsService

invoice_router = APIRouter()


@invoice_router.post("/", response_model=ResponseSchema[InvoiceOut])
async def create_invoice(
    invoice_in: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = InvoicesService(db)
    data = await service.create(invoice_in)
    return success_response(data=data)


@invoice_router.get("/", response_model=ResponseSchema[list[InvoiceOut]])
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = InvoicesService(db)
    data = await service.list()
    return success_response(data=data)


@invoice_router.get(
    "/payment-methods", response_model=ResponseSchema[list[PaymentMethodOut]]
)
async def list_payment_methods(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PaymentsService(db)
    data = await service.list_methods()
    return success_response(data=data)


@invoice_router.post("/payments/", response_model=ResponseSchema[PaymentOut])
async def register_payment(
    payment_in: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PaymentsService(db)
    payment = await service.create(payment_in)
    data = PaymentOut.model_validate(payment).model_dump()
    return success_response(data=data)


@invoice_router.post(
    "/bank-checks/{check_id}/exchange", response_model=ResponseSchema[BankCheckOut]
)
async def exchange_bank_check(
    check_id: int,
    exchange_in: BankCheckExchange,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = BankChecksService(db)
    check = await service.mark_as_exchanged(check_id, exchange_in)
    data = BankCheckOut.model_validate(check).model_dump()
    return success_response(data=data)


@invoice_router.get("/payments/{invoice_id}/total", response_model=ResponseSchema[dict])
async def total_paid(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PaymentsService(db)
    total = await service.total_by_invoice(invoice_id)
    return success_response(data={"total": total})


@invoice_router.get(
    "/payments/{invoice_id}", response_model=ResponseSchema[list[PaymentOut]]
)
async def list_payments(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PaymentsService(db)
    data = await service.list_by_invoice(invoice_id)
    return success_response(data=data)


@invoice_router.get(
    "/{invoice_id}/detail", response_model=ResponseSchema[InvoiceDetailOut]
)
async def get_invoice_detail(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = InvoicesService(db)
    data = await service.detail(invoice_id)
    return success_response(data=data)


@invoice_router.get("/{invoice_id}", response_model=ResponseSchema[InvoiceOut])
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = InvoicesService(db)
    data = await service.get(invoice_id)
    return success_response(data=data)


@invoice_router.put("/{invoice_id}", response_model=ResponseSchema[InvoiceOut])
async def update_invoice(
    invoice_id: int,
    invoice_in: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = InvoicesService(db)
    data = await service.update(invoice_id, invoice_in)
    return success_response(data=data)
