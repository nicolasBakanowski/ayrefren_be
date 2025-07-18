import asyncio

from app.models.clients import Client, ClientType
from app.models.trucks import Truck
from app.models.work_orders import WorkOrderStatus, WorkOrder
from app.models.invoices import (
    Invoice,
    InvoiceStatus,
    InvoiceType,
    PaymentMethod,
)


def _seed_invoice(session_factory):
    async def run():
        async with session_factory() as session:
            client = Client(type=ClientType.persona, name="Payer")
            session.add(client)
            await session.flush()

            truck = Truck(client_id=client.id, license_plate="PAY111")
            status = WorkOrderStatus(name="open")
            session.add_all([truck, status])
            await session.flush()

            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            inv_status = InvoiceStatus(name="pending")
            inv_type = InvoiceType(name="A")
            session.add_all([order, inv_status, inv_type])
            await session.flush()

            invoice = Invoice(
                work_order_id=order.id,
                client_id=client.id,
                invoice_type_id=inv_type.id,
                status_id=inv_status.id,
                labor_total=0,
                parts_total=0,
                iva=0,
                total=100,
            )
            method = PaymentMethod(name="Cash")
            session.add_all([invoice, method])
            await session.commit()
            await session.refresh(invoice)
            await session.refresh(method)
            return invoice.id, method.id

    return asyncio.run(run())


def test_list_payment_methods(client):
    http, session_factory = client

    async def seed():
        async with session_factory() as session:
            session.add(PaymentMethod(name="Cash"))
            await session.commit()

    asyncio.run(seed())

    resp = http.get("/invoices/payment-methods")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Cash"


def test_total_paid(client):
    http, session_factory = client
    invoice_id, method_id = _seed_invoice(session_factory)

    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method_id, "amount": 40},
    )
    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method_id, "amount": 60},
    )

    resp = http.get(f"/invoices/payments/{invoice_id}/total")
    assert resp.status_code == 200
    assert resp.json()["total"] == 100


def test_partial_payments_different_methods(client):
    http, session_factory = client
    invoice_id, method1_id = _seed_invoice(session_factory)

    async def create_method():
        async with session_factory() as session:
            method = PaymentMethod(name="Card")
            session.add(method)
            await session.commit()
            await session.refresh(method)
            return method.id

    method2_id = asyncio.run(create_method())

    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method1_id, "amount": 30},
    )
    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method2_id, "amount": 70},
    )

    resp = http.get(f"/invoices/payments/{invoice_id}")
    assert resp.status_code == 200
    payments = resp.json()
    assert len(payments) == 2
    assert {p["method_id"] for p in payments} == {method1_id, method2_id}

    resp = http.get(f"/invoices/{invoice_id}")
    assert resp.status_code == 200
    assert resp.json()["paid"] == 100

    resp = http.get(f"/invoices/payments/{invoice_id}/total")
    assert resp.status_code == 200
    assert resp.json()["total"] == 100

