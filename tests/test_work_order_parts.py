import asyncio

def test_add_work_order_invalid_fk(client):
    http, _ = client
    resp = http.post(
        "/work-orders/parts/",
        json={
            "work_order_id": 999,
            "quantity": 1,
            "name": "Test Part",
            "unit_price": 10,
            "subtotal": 10,
            "increment_per_unit": 20,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]
    assert data["code"] == 404


def test_list_part_names(client):
    http, session_factory = client

    async def seed_data():
        async with session_factory() as session:
            from app.models.clients import Client, ClientType
            from app.models.trucks import Truck
            from app.models.work_orders import WorkOrder, WorkOrderStatus
            from app.models.work_order_parts import WorkOrderPart

            cli = Client(type=ClientType.persona, name="Parts")
            session.add(cli)
            await session.flush()

            truck = Truck(client_id=cli.id, license_plate="P123")
            status = WorkOrderStatus(name="open")
            session.add_all([truck, status])
            await session.flush()

            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.flush()

            part1 = WorkOrderPart(
                work_order_id=order.id,
                name="Filter",
                quantity=1,
                unit_price=10,
                subtotal=10,
                increment_per_unit=0,
            )
            part2 = WorkOrderPart(
                work_order_id=order.id,
                name="Bolt",
                quantity=2,
                unit_price=5,
                subtotal=10,
                increment_per_unit=0,
            )
            part3 = WorkOrderPart(
                work_order_id=order.id,
                name="Filter",
                quantity=1,
                unit_price=10,
                subtotal=10,
                increment_per_unit=0,
            )
            session.add_all([part1, part2, part3])
            await session.commit()
            await session.refresh(order)
            return order.id

    order_id = asyncio.run(seed_data())

    resp = http.get(f"/work-orders/parts/names?work_order_id={order_id}")
    assert resp.status_code == 200
    names = resp.json()["data"]
    assert set(names) == {"Filter", "Bolt"}


def test_list_all_part_names(client):
    http, session_factory = client

    async def seed_data():
        async with session_factory() as session:
            from app.models.clients import Client, ClientType
            from app.models.trucks import Truck
            from app.models.work_orders import WorkOrder, WorkOrderStatus
            from app.models.work_order_parts import WorkOrderPart

            cli = Client(type=ClientType.persona, name="PartsAll")
            session.add(cli)
            await session.flush()

            truck = Truck(client_id=cli.id, license_plate="P999")
            status = WorkOrderStatus(name="open")
            session.add_all([truck, status])
            await session.flush()

            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.flush()

            part1 = WorkOrderPart(
                work_order_id=order.id,
                name="Wheel",
                quantity=1,
                unit_price=10,
                subtotal=10,
                increment_per_unit=0,
            )
            session.add(part1)
            await session.commit()

    asyncio.run(seed_data())

    resp = http.get("/work-orders/parts/names")
    assert resp.status_code == 200
    names = resp.json()["data"]
    assert "Wheel" in names
