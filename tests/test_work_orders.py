import asyncio

from app.models.clients import Client, ClientType
from app.models.trucks import Truck
from app.models.users import Role, User
from app.models.work_orders import WorkOrder, WorkOrderStatus


def test_create_order_invalid_truck(client):
    http, _ = client
    resp = http.post(
        "/orders/",
        json={
            "truck_id": -1,
            "status_id": -1,
            "notes": "Test order",
            "fast_phone": "1234567890",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]
    assert data["code"] == 404


def test_update_order_invalid_status(client):
    http, session_factory = client

    async def seed_order():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="Test")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="XYZ")
            session.add(truck)
            status = WorkOrderStatus(name="new")
            session.add(status)
            await session.flush()
            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order.id

    order_id = asyncio.run(seed_order())
    resp = http.put(f"/orders/{order_id}", json={"status_id": 999})
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]
    assert data["code"] == 404


def test_create_order_success(client):
    http, session_factory = client

    async def seed_refs():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="Creator")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="AAA111")
            session.add(truck)
            status = WorkOrderStatus(name="open")
            session.add(status)
            await session.commit()
            await session.refresh(truck)
            await session.refresh(status)
            return truck.id, status.id

    truck_id, status_id = asyncio.run(seed_refs())
    resp = http.post(
        "/orders/",
        json={"truck_id": truck_id, "status_id": status_id, "notes": "Test"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["truck_id"] == truck_id
    assert data["status_id"] == status_id


def test_list_orders(client):
    http, session_factory = client

    async def seed_orders():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="Lister")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="LIST111")
            session.add(truck)
            status = WorkOrderStatus(name="lst")
            session.add(status)
            await session.flush()
            for _ in range(2):
                order = WorkOrder(truck_id=truck.id, status_id=status.id)
                session.add(order)
            await session.commit()

    asyncio.run(seed_orders())
    resp = http.get("/orders/")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


def test_list_orders_pagination(client):
    http, session_factory = client

    async def seed_orders():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="Paginator")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="PAG111")
            session.add(truck)
            status = WorkOrderStatus(name="pg")
            session.add(status)
            await session.flush()
            ids = []
            for _ in range(3):
                order = WorkOrder(truck_id=truck.id, status_id=status.id)
                session.add(order)
                await session.flush()
                ids.append(order.id)
            await session.commit()
            return ids

    ids = asyncio.run(seed_orders())
    resp = http.get("/orders/", params={"skip": 1, "limit": 1})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == ids[1]


def test_get_order_success(client):
    http, session_factory = client

    async def seed_order():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="Getter")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="GET111")
            session.add(truck)
            status = WorkOrderStatus(name="pending")
            session.add(status)
            await session.flush()
            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order.id

    order_id = asyncio.run(seed_order())
    resp = http.get(f"/orders/{order_id}")
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["id"] == order_id
    assert body["is_editable"] is True


def test_get_order_not_editable_with_invoice(client):
    http, session_factory = client

    async def seed_invoice():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="InvClient")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="INV111")
            session.add(truck)
            status = WorkOrderStatus(name="pending")
            session.add(status)
            await session.flush()
            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.flush()
            from app.models.invoices import Invoice, InvoiceStatus, InvoiceType

            inv_status = InvoiceStatus(name="pend")
            inv_type = InvoiceType(name="A")
            session.add_all([inv_status, inv_type])
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
            await session.commit()
            await session.refresh(order)
            return order.id

    order_id = asyncio.run(seed_invoice())
    resp = http.get(f"/orders/{order_id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["is_editable"] is False


def test_update_order_success(client):
    http, session_factory = client

    async def seed_data():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="Updater")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="UPD111")
            session.add(truck)
            status1 = WorkOrderStatus(name="open")
            status2 = WorkOrderStatus(name="closed")
            session.add_all([status1, status2])
            await session.flush()
            order = WorkOrder(truck_id=truck.id, status_id=status1.id)
            session.add(order)
            await session.commit()
            await session.refresh(order)
            await session.refresh(status2)
            return order.id, status2.id

    order_id, new_status_id = asyncio.run(seed_data())
    resp = http.put(f"/orders/{order_id}", json={"status_id": new_status_id})
    assert resp.status_code == 200
    assert resp.json()["data"]["status_id"] == new_status_id


def test_delete_order_success(client):
    http, session_factory = client

    async def seed_order():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="Deleter")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="DEL111")
            session.add(truck)
            status = WorkOrderStatus(name="to-delete")
            session.add(status)
            await session.flush()
            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order.id

    order_id = asyncio.run(seed_order())
    resp = http.delete(f"/orders/{order_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["detail"] == "Orden eliminada"


def test_assign_and_remove_reviewer(client):
    http, session_factory = client

    async def seed_data():
        async with session_factory() as session:
            role = Role(name="rev")
            session.add(role)
            await session.flush()
            reviewer = User(
                name="Reviewer",
                email="rev@example.com",
                password="x",
                role_id=role.id,
            )
            session.add(reviewer)
            cli = Client(type=ClientType.persona, name="Client")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="REV111")
            session.add(truck)
            status = WorkOrderStatus(name="assigned")
            session.add(status)
            await session.flush()
            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.commit()
            await session.refresh(order)
            await session.refresh(reviewer)
            return order.id, reviewer.id

    order_id, reviewer_id = asyncio.run(seed_data())
    resp = http.post(
        "/work-orders/reviewer/",
        json={"work_order_id": order_id, "reviewer_id": reviewer_id},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["reviewed_by"] == reviewer_id

    resp = http.delete(f"/work-orders/reviewer/{order_id}/{reviewer_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["reviewed_by"] is None


def test_order_total_with_increments(client):
    http, session_factory = client

    async def seed_data():
        async with session_factory() as session:
            from app.models.clients import Client, ClientType
            from app.models.trucks import Truck
            from app.models.users import Role, User
            from app.models.work_order_parts import WorkOrderPart
            from app.models.work_order_tasks import WorkOrderTask
            from app.models.work_orders import WorkOrder, WorkOrderStatus
            from app.models.work_orders_mechanic import WorkArea

            cli = Client(type=ClientType.persona, name="Total")
            role = Role(name="worker")
            area = WorkArea(name="area")
            session.add_all([cli, role, area])
            await session.flush()
            user = User(name="U", email="u@a.com", password="x", role_id=role.id)
            session.add(user)
            await session.flush()

            truck = Truck(client_id=cli.id, license_plate="TOT111")
            status = WorkOrderStatus(name="open")
            session.add_all([truck, status])
            await session.flush()

            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.flush()

            wop = WorkOrderPart(
                work_order_id=order.id,
                name="part.id",
                quantity=2,
                unit_price=10,
                subtotal=20,
                increment_per_unit=10,
            )
            task = WorkOrderTask(
                work_order_id=order.id,
                user_id=user.id,
                area_id=area.id,
                description="fix",
                price=30,
                external=False,
            )
            session.add_all([wop, task])
            await session.commit()
            await session.refresh(order)
            return order.id

    order_id = asyncio.run(seed_data())
    resp = http.get(f"/orders/{order_id}/total")

    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 52
