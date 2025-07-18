from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import validate_foreign_keys
from app.db.repositories.invoices import InvoicesRepository, PaymentsRepository
from app.models.clients import Client
from app.models.invoices import Invoice, InvoiceStatus, InvoiceType, PaymentMethod
from app.models.work_orders import WorkOrder
from app.schemas.invoices import InvoiceCreate, PaymentCreate, InvoiceOut


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

    async def list(self):
        return await self.repo.list()


class PaymentsService:
    def __init__(self, db: AsyncSession):
        self.repo = PaymentsRepository(db)

    async def create(self, data: PaymentCreate):
        await validate_foreign_keys(
            self.repo.db,
            {Invoice: data.invoice_id, PaymentMethod: data.method_id},
        )
        return await self.repo.create(data)

    async def list_by_invoice(self, invoice_id: int):
        return await self.repo.list_by_invoice(invoice_id)

    async def total_by_invoice(self, invoice_id: int) -> float:
        return await self.repo.total_by_invoice(invoice_id)

    async def list_methods(self):
        return await self.repo.list_methods()
