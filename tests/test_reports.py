import asyncio
from datetime import datetime

from app.models.clients import Client, ClientType
from app.models.invoices import (
    Invoice,
    InvoiceStatus,
    InvoiceType,
    Payment,
    PaymentMethod,
)
from app.models.trucks import Truck
from app.models.work_orders import WorkOrder, WorkOrderStatus


def _seed_data(session_factory):
    async def run():
        async with session_factory() as session:
            c1 = Client(type=ClientType.persona, name="Alpha")
            c2 = Client(type=ClientType.persona, name="Beta")
            session.add_all([c1, c2])
            await session.flush()

            truck1 = Truck(client_id=c1.id, license_plate="A111")
            truck2 = Truck(client_id=c2.id, license_plate="B222")
            status = WorkOrderStatus(name="rpt")
            session.add_all([truck1, truck2, status])
            await session.flush()

            order1 = WorkOrder(truck_id=truck1.id, status_id=status.id)
            order2 = WorkOrder(truck_id=truck2.id, status_id=status.id)
            inv_status = InvoiceStatus(name="pending")
            inv_type = InvoiceType(name="A", surcharge=21)
            session.add_all([order1, order2, inv_status, inv_type])
            await session.flush()

            invoice1 = Invoice(
                work_order_id=order1.id,
                client_id=c1.id,
                invoice_type_id=inv_type.id,
                status_id=inv_status.id,
                labor_total=0,
                parts_total=0,
                iva=0,
                total=100,
                issued_at=datetime(2024, 1, 10),
            )
            invoice2 = Invoice(
                work_order_id=order2.id,
                client_id=c2.id,
                invoice_type_id=inv_type.id,
                status_id=inv_status.id,
                labor_total=0,
                parts_total=0,
                iva=0,
                total=200,
                issued_at=datetime(2024, 2, 10),
            )
            method = PaymentMethod(name="Cash")
            session.add_all([invoice1, invoice2, method])
            await session.flush()

            payment1 = Payment(
                invoice_id=invoice1.id,
                method_id=method.id,
                amount=100,
                date=datetime(2024, 1, 20),
            )
            payment2 = Payment(
                invoice_id=invoice2.id,
                method_id=method.id,
                amount=200,
                date=datetime(2024, 2, 20),
            )
            session.add_all([payment1, payment2])
            await session.commit()
            await session.refresh(c1)
            await session.refresh(c2)
            return c1.id, c2.id

    return asyncio.run(run())


def test_billing_by_client_date_range(client):
    http, session_factory = client
    client1_id, _ = _seed_data(session_factory)

    resp = http.get(
        "/reports/billing-by-client",
        params={"start_date": "2024-01-01", "end_date": "2024-01-31"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["client_id"] == client1_id
    assert data[0]["total_billed"] == 100


def test_payments_by_method_filters(client):
    http, session_factory = client
    client1_id, _ = _seed_data(session_factory)

    resp = http.get(
        "/reports/payments-by-method",
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "client_id": client1_id,
        },
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["method"] == "Cash"
    assert data[0]["total_received"] == 100
