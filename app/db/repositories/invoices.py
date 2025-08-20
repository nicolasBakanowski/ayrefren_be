from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.invoices import BankCheck, Invoice, Payment, PaymentMethod
from app.models.work_orders import WorkOrder
from app.schemas.invoices import InvoiceCreate, InvoiceUpdate, PaymentCreate


class InvoicesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: InvoiceCreate) -> Invoice:
        invoice = Invoice(**data.model_dump())
        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice

    async def get(self, id: int) -> Invoice | None:
        result = await self.db.execute(
            select(Invoice)
            .options(
                selectinload(Invoice.invoice_type),
                selectinload(Invoice.client),
                selectinload(Invoice.status),
                selectinload(Invoice.payments).selectinload(Payment.bank_checks),
                selectinload(Invoice.payments).selectinload(Payment.method),
            )
            .where(Invoice.id == id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, skip: int = 0, limit: int = 100, status_id: int | None = None
    ) -> list[Invoice]:
        query = (
            select(Invoice)
            .options(
                selectinload(Invoice.client),
                selectinload(Invoice.invoice_type),
                selectinload(Invoice.status),
            )
            .order_by(Invoice.id.desc())
            .offset(skip)
            .limit(limit)
        )
        if status_id is not None:
            query = query.where(Invoice.status_id == status_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, id: int, data: InvoiceUpdate) -> Invoice:
        invoice = await self.get(id)
        if not invoice:
            return False

        data = data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(invoice, key, value)
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice

    async def mark_as_accepted(self, invoice_id: int) -> Invoice | None:
        """Mark invoice as accepted and return it with relationships loaded."""
        invoice = await self.db.get(Invoice, invoice_id)
        if not invoice:
            return None
        invoice.accepted = True
        await self.db.commit()
        # reload with eager relationships to avoid lazy loading later
        return await self.get(invoice_id)


class PaymentsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: PaymentCreate) -> Payment:
        bank_checks_data = data.bank_checks or []
        payment_dict = data.model_dump(exclude={"bank_checks"})
        payment = Payment(**payment_dict)
        self.db.add(payment)
        await self.db.flush()
        for bc in bank_checks_data:
            self.db.add(BankCheck(payment_id=payment.id, **bc.model_dump()))

        # Actualizar total pagado en la factura
        invoice = await self.db.get(Invoice, data.invoice_id)
        invoice.paid = (invoice.paid or Decimal("0")) + Decimal(str(data.amount))

        await self.db.commit()
        return await self.get(payment.id)

    async def get(self, payment_id: int) -> Payment | None:
        result = await self.db.execute(
            select(Payment)
            .options(
                selectinload(Payment.bank_checks),
                selectinload(Payment.method),
                selectinload(Payment.invoice)
                .selectinload(Invoice.work_order)
                .selectinload(WorkOrder.reviewer),
                selectinload(Payment.invoice),
                selectinload(Payment.method),
            )
            .where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def list_by_invoice(
        self, invoice_id: int, skip: int = 0, limit: int = 100
    ) -> list[Payment]:
        result = await self.db.execute(
            select(Payment)
            .options(
                selectinload(Payment.bank_checks),
                selectinload(Payment.method),
            )
            .where(Payment.invoice_id == invoice_id)
            .offset(skip)
            .limit(limit)
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

    async def get_bank_check(self, check_id: int) -> BankCheck | None:
        result = await self.db.execute(
            select(BankCheck).where(BankCheck.id == check_id)
        )
        return result.scalar_one_or_none()

    async def mark_check_as_exchanged(
        self, check_id: int, exchange_date: datetime
    ) -> BankCheck | None:
        check = await self.db.get(BankCheck, check_id)
        if not check:
            return None
        check.exchange_date = exchange_date
        await self.db.commit()
        await self.db.refresh(check)
        return check

    async def list(
        self,
        client_id: int | None = None,
        invoice_id: int | None = None,
        payment_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Payment]:
        """Return payments filtered by client and/or invoice."""
        query = select(Payment).options(
            selectinload(Payment.bank_checks),
            selectinload(Payment.method),
            selectinload(Payment.invoice).selectinload(Invoice.client),
            selectinload(Payment.invoice).selectinload(Invoice.invoice_type),
            selectinload(Payment.invoice).selectinload(Invoice.status),
        )
        if client_id is not None:
            query = query.join(Payment.invoice).where(Invoice.client_id == client_id)
        if invoice_id is not None:
            query = query.where(Payment.invoice_id == invoice_id)
        if payment_type is not None:
            if payment_type.lower() in {"physical", "electronic"}:
                query = query.join(Payment.bank_checks).where(
                    BankCheck.type == payment_type
                )
            else:
                query = query.join(Payment.method).where(
                    PaymentMethod.name == payment_type
                )
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
