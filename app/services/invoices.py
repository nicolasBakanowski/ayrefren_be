from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.invoices import InvoicesRepository, PaymentsRepository
from app.schemas.invoices import InvoiceCreate, PaymentCreate


class InvoicesService:
    def __init__(self, db: AsyncSession):
        self.repo = InvoicesRepository(db)

    async def create(self, data: InvoiceCreate):
        return await self.repo.create(data)

    async def get(self, invoice_id: int):
        invoice = await self.repo.get(invoice_id)
        if not invoice:
            raise HTTPException(404, detail="Factura no encontrada")
        return invoice

    async def list(self):
        return await self.repo.list()


class PaymentsService:
    def __init__(self, db: AsyncSession):
        self.repo = PaymentsRepository(db)

    async def create(self, data: PaymentCreate):
        return await self.repo.create(data)

    async def list_by_invoice(self, invoice_id: int):
        return await self.repo.list_by_invoice(invoice_id)
