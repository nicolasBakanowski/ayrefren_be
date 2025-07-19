import asyncio

from app.models.clients import Client, ClientType
from app.models.invoices import Invoice, InvoiceStatus, InvoiceType


def test_create_invoice_invalid_order(client):
    http, session_factory = client

    async def setup_refs():
        async with session_factory() as session:
            client_obj = Client(type=ClientType.persona, name="Test")
            status = InvoiceStatus(name="pending")
            inv_type = InvoiceType(name="type1", surcharge=0)
            session.add_all([client_obj, status, inv_type])
            await session.commit()
            await session.refresh(client_obj)
            await session.refresh(status)
            await session.refresh(inv_type)
            return client_obj.id, inv_type.id, status.id

    cli_id, inv_type_id, status_id = asyncio.run(setup_refs())
    resp = http.post(
        "/invoices/",
        json={
            "work_order_id": 123,
            "client_id": cli_id,
            "invoice_type_id": inv_type_id,
            "status_id": status_id,
            "labor_total": 0,
            "parts_total": 0,
            "iva": 0,
            "total": 0,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]
    assert data["code"] == 404


def test_invoice_detail_with_surcharge(client):
    http, session_factory = client

    async def seed():
        async with session_factory() as session:
            client_obj = Client(type=ClientType.persona, name="Det")
            status = InvoiceStatus(name="pending")
            inv_type = InvoiceType(name="A", surcharge=21)
            session.add_all([client_obj, status, inv_type])
            await session.flush()

            from app.models.trucks import Truck
            from app.models.work_orders import WorkOrder, WorkOrderStatus

            truck = Truck(client_id=client_obj.id, license_plate="DET111")
            wo_status = WorkOrderStatus(name="open")
            session.add_all([truck, wo_status])
            await session.flush()

            order = WorkOrder(truck_id=truck.id, status_id=wo_status.id)
            session.add(order)
            await session.flush()

            invoice = Invoice(
                work_order_id=order.id,
                client_id=client_obj.id,
                invoice_type_id=inv_type.id,
                status_id=status.id,
                labor_total=0,
                parts_total=0,
                iva=0,
                total=100,
            )
            session.add(invoice)
            await session.commit()
            await session.refresh(invoice)
            return invoice.id

    invoice_id = asyncio.run(seed())
    resp = http.get(f"/invoices/{invoice_id}/detail")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_without_surcharge"] == 100
    assert data["total_with_surcharge"] == 121
