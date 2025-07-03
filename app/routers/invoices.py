from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.schemas.invoices import InvoiceCreate, InvoiceOut, PaymentCreate, PaymentOut
from app.services.invoices import InvoicesService, PaymentsService

invoice_router = APIRouter()


@invoice_router.post("/", response_model=InvoiceOut, dependencies=[Depends(roles_allowed("admin", "revisor"))])
async def create_invoice(invoice_in: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    service = InvoicesService(db)
    return await service.create(invoice_in)


@invoice_router.get("/", response_model=list[InvoiceOut], dependencies=[Depends(roles_allowed("admin", "revisor"))])
async def list_invoices(db: AsyncSession = Depends(get_db)):
    service = InvoicesService(db)
    return await service.list()


@invoice_router.get("/{invoice_id}", response_model=InvoiceOut,
                    dependencies=[Depends(roles_allowed("admin", "revisor"))])
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    service = InvoicesService(db)
    return await service.get(invoice_id)


@invoice_router.post("/payments/", response_model=PaymentOut, dependencies=[Depends(roles_allowed("admin", "revisor"))])
async def register_payment(payment_in: PaymentCreate, db: AsyncSession = Depends(get_db)):
    service = PaymentsService(db)
    return await service.create(payment_in)


@invoice_router.get("/payments/{invoice_id}", response_model=list[PaymentOut],
                    dependencies=[Depends(roles_allowed("admin", "revisor"))])
async def list_payments(invoice_id: int, db: AsyncSession = Depends(get_db)):
    service = PaymentsService(db)
    return await service.list_by_invoice(invoice_id)
