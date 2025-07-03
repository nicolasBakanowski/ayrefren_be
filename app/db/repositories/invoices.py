from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.invoices import Invoice, Payment
from app.schemas.invoices import InvoiceCreate, PaymentCreate


class InvoicesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: InvoiceCreate) -> Invoice:
        invoice = Invoice(**data.dict())
        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice

    async def get(self, id: int) -> Invoice | None:
        result = await self.db.execute(select(Invoice).where(Invoice.id == id))
        return result.scalar_one_or_none()

    async def list(self) -> list[Invoice]:
        result = await self.db.execute(select(Invoice))
        return result.scalars().all()


class PaymentsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: PaymentCreate) -> Payment:
        payment = Payment(**data.dict())
        self.db.add(payment)

        # Actualizar total pagado en la factura
        invoice = await self.db.get(Invoice, data.invoice_id)
        invoice.paid += data.amount

        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def list_by_invoice(self, invoice_id: int) -> list[Payment]:
        result = await self.db.execute(
            select(Payment).where(Payment.invoice_id == invoice_id)
        )
        return result.scalars().all()
