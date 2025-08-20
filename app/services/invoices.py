from fastapi import HTTPException
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import exists_or_404, validate_foreign_keys
from app.db.repositories.invoices import InvoicesRepository, PaymentsRepository
from app.models.clients import Client
from app.models.invoices import (
    BankCheck,
    Invoice,
    InvoiceStatus,
    InvoiceType,
    Payment,
    PaymentMethod,
)
from app.models.work_orders import WorkOrder
from app.schemas.invoices import (
    BankCheckExchange,
    InvoiceCreate,
    InvoiceOut,
    InvoiceUpdate,
    PaymentCreate,
)
from app.services.notifications import NotificationService


def _invoice_with_surcharge(invoice: Invoice) -> dict:
    surcharge = float(invoice.invoice_type.surcharge or 0)
    base_total = float(invoice.total)
    data = InvoiceOut.model_validate(invoice).model_dump()
    data.update(
        {
            "surcharge": surcharge,
            "total_without_surcharge": base_total,
            "total_with_surcharge": base_total * (1 + surcharge / 100),
        }
    )
    return data


class InvoicesService:
    def __init__(self, db: AsyncSession):
        self.repo = InvoicesRepository(db)

    async def create(self, data: InvoiceCreate):
        await validate_foreign_keys(
            self.repo.db,
            {
                WorkOrder: data.work_order_id,
                Client: data.client_id,
                InvoiceType: data.invoice_type_id,
                InvoiceStatus: data.status_id,
            },
        )
        return await self.repo.create(data)

    async def get(self, invoice_id: int):
        invoice = await self.repo.get(invoice_id)
        if not invoice:
            raise HTTPException(404, detail="Factura no encontrada")
        return invoice

    async def detail(self, invoice_id: int):
        invoice = await self.get(invoice_id)
        return _invoice_with_surcharge(invoice)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        client_id: int | None = None,
    ):
        return await self.repo.list(
            skip=skip,
            limit=limit,
            status_id=status_id,
            start_date=start_date,
            end_date=end_date,
            client_id=client_id,
        )

    async def update(self, invoice_id: int, data: InvoiceUpdate):
        await exists_or_404(self.repo.db, Invoice, invoice_id)
        if data.status_id is not None:
            await exists_or_404(self.repo.db, InvoiceStatus, data.status_id)

        if data.invoice_type_id is not None:
            await exists_or_404(self.repo.db, InvoiceType, data.invoice_type_id)

        invoice = await self.repo.update(invoice_id, data)
        if not invoice:
            raise HTTPException(404, detail="Factura no encontrada")
        return _invoice_with_surcharge(invoice)

    async def mark_as_accepted(self, invoice_id: int):
        invoice = await self.repo.mark_as_accepted(invoice_id)
        if not invoice:
            raise HTTPException(404, detail="Factura no encontrada")
        return _invoice_with_surcharge(invoice)


class PaymentsService:
    def __init__(self, db: AsyncSession):
        self.repo = PaymentsRepository(db)
        self.notifier = NotificationService(db)

    async def create(self, data: PaymentCreate):
        await validate_foreign_keys(
            self.repo.db,
            {Invoice: data.invoice_id, PaymentMethod: data.method_id},
        )
        payment = await self.repo.create(data)
        for check in payment.bank_checks:
            if check.due_date:
                await self.notifier.notify_due_check(check)
        return payment

    async def list_by_invoice(self, invoice_id: int, skip: int = 0, limit: int = 100):
        return await self.repo.list_by_invoice(invoice_id, skip=skip, limit=limit)

    async def list(
        self,
        client_id: int | None = None,
        invoice_id: int | None = None,
        payment_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Payment]:
        return await self.repo.list(
            client_id=client_id,
            invoice_id=invoice_id,
            payment_type=payment_type,
            skip=skip,
            limit=limit,
        )

    async def total_by_invoice(self, invoice_id: int) -> float:
        return await self.repo.total_by_invoice(invoice_id)

    async def list_methods(self):
        return await self.repo.list_methods()


class BankChecksService:
    def __init__(self, db: AsyncSession):
        self.repo = PaymentsRepository(db)

    async def mark_as_exchanged(
        self, check_id: int, data: BankCheckExchange
    ) -> BankCheck:
        check = await self.repo.mark_check_as_exchanged(check_id, data.exchange_date)
        if not check:
            raise HTTPException(status_code=404, detail="Cheque no encontrado")
        return check
