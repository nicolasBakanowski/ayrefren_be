import asyncio
from datetime import datetime

from app.models.clients import Client, ClientType
from app.models.invoices import Invoice, InvoiceStatus, InvoiceType
from app.models.trucks import Truck
from app.models.work_orders import WorkOrder, WorkOrderStatus


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
    data = resp.json()["data"]
    assert data["total_without_surcharge"] == 100
    assert data["total_with_surcharge"] == 121


def test_list_invoices_pagination(client):
    http, session_factory = client

    async def seed_invoices():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="InvLister")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="INV111")
            session.add(truck)
            wo_status = WorkOrderStatus(name="open")
            inv_status = InvoiceStatus(name="pending")
            inv_type = InvoiceType(name="A", surcharge=0)
            session.add_all([wo_status, inv_status, inv_type])
            await session.flush()
            ids = []
            for _ in range(3):
                order = WorkOrder(truck_id=truck.id, status_id=wo_status.id)
                session.add(order)
                await session.flush()
                invoice = Invoice(
                    work_order_id=order.id,
                    client_id=cli.id,
                    invoice_type_id=inv_type.id,
                    status_id=inv_status.id,
                    labor_total=0,
                    parts_total=0,
                    iva=0,
                    total=0,
                )
                session.add(invoice)
                await session.flush()
                ids.append(invoice.id)
            await session.commit()
            return ids

    ids = asyncio.run(seed_invoices())
    resp = http.get("/invoices/")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert [inv["id"] for inv in data[:3]] == ids[::-1]

    resp = http.get("/invoices/", params={"skip": 1, "limit": 1})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == ids[-2]


def test_list_invoices_by_status(client):
    http, session_factory = client

    async def seed():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="InvFilter")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="FIL111")
            session.add(truck)
            wo_status = WorkOrderStatus(name="open")
            inv_status1 = InvoiceStatus(name="pending")
            inv_status2 = InvoiceStatus(name="paid")
            inv_type = InvoiceType(name="A", surcharge=0)
            session.add_all([wo_status, inv_status1, inv_status2, inv_type])
            await session.flush()

            order1 = WorkOrder(truck_id=truck.id, status_id=wo_status.id)
            session.add(order1)
            await session.flush()
            session.add(
                Invoice(
                    work_order_id=order1.id,
                    client_id=cli.id,
                    invoice_type_id=inv_type.id,
                    status_id=inv_status1.id,
                    labor_total=0,
                    parts_total=0,
                    iva=0,
                    total=0,
                )
            )

            order2 = WorkOrder(truck_id=truck.id, status_id=wo_status.id)
            session.add(order2)
            await session.flush()
            inv2 = Invoice(
                work_order_id=order2.id,
                client_id=cli.id,
                invoice_type_id=inv_type.id,
                status_id=inv_status2.id,
                labor_total=0,
                parts_total=0,
                iva=0,
                total=0,
            )
            session.add(inv2)
            await session.commit()
            return inv_status2.id, inv2.id

    status_id, invoice_id = asyncio.run(seed())
    resp = http.get("/invoices/", params={"status_id": status_id})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == invoice_id


def test_list_invoices_by_client_and_date(client):
    http, session_factory = client

    async def seed():
        async with session_factory() as session:
            cli1 = Client(type=ClientType.persona, name="I1")
            cli2 = Client(type=ClientType.persona, name="I2")
            session.add_all([cli1, cli2])
            await session.flush()
            truck1 = Truck(client_id=cli1.id, license_plate="TIN1")
            truck2 = Truck(client_id=cli2.id, license_plate="TIN2")
            session.add_all([truck1, truck2])
            wo_status = WorkOrderStatus(name="open")
            inv_status = InvoiceStatus(name="pending")
            inv_type = InvoiceType(name="A", surcharge=0)
            session.add_all([wo_status, inv_status, inv_type])
            await session.flush()

            order1 = WorkOrder(truck_id=truck1.id, status_id=wo_status.id)
            order2 = WorkOrder(truck_id=truck2.id, status_id=wo_status.id)
            session.add_all([order1, order2])
            await session.flush()

            inv1 = Invoice(
                work_order_id=order1.id,
                client_id=cli1.id,
                invoice_type_id=inv_type.id,
                status_id=inv_status.id,
                labor_total=0,
                parts_total=0,
                iva=0,
                total=0,
                issued_at=datetime(2023, 1, 1),
            )
            inv2 = Invoice(
                work_order_id=order2.id,
                client_id=cli2.id,
                invoice_type_id=inv_type.id,
                status_id=inv_status.id,
                labor_total=0,
                parts_total=0,
                iva=0,
                total=0,
                issued_at=datetime(2023, 2, 1),
            )
            session.add_all([inv1, inv2])
            await session.commit()
            await session.refresh(inv1)
            await session.refresh(inv2)
            return cli1.id, inv1.id, inv2.id

    client_id, inv1_id, inv2_id = asyncio.run(seed())

    resp = http.get("/invoices/", params={"client_id": client_id})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1 and data[0]["id"] == inv1_id

    resp = http.get(
        "/invoices/",
        params={
            "start_date": datetime(2023, 1, 15).isoformat(),
            "end_date": datetime(2023, 2, 15).isoformat(),
        },
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1 and data[0]["id"] == inv2_id
