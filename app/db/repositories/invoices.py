from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from sqlalchemy import select, func
from app.models.invoices import Invoice, Payment, BankCheck, PaymentMethod
from app.schemas.invoices import InvoiceCreate, PaymentCreate, BankCheckIn


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
        bank_checks_data = data.bank_checks or []
        payment_dict = data.dict(exclude={"bank_checks"})
        payment = Payment(**payment_dict)
        self.db.add(payment)
        await self.db.flush()
        for bc in bank_checks_data:
            self.db.add(BankCheck(payment_id=payment.id, **bc))

        # Actualizar total pagado en la factura
        invoice = await self.db.get(Invoice, data.invoice_id)
        invoice.paid = (invoice.paid or Decimal("0")) + Decimal(str(data.amount))

        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def list_by_invoice(self, invoice_id: int) -> list[Payment]:
        result = await self.db.execute(
            select(Payment).where(Payment.invoice_id == invoice_id)
        )
        return result.scalars().all()

    async def total_by_invoice(self, invoice_id: int) -> float:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.invoice_id == invoice_id
            )
        )
        return float(result.scalar_one())

    async def list_methods(self) -> list[PaymentMethod]:
        result = await self.db.execute(select(PaymentMethod))
        return result.scalars().all()
