import asyncio
from app.models.clients import Client, ClientType
from app.models.trucks import Truck
from app.models.work_orders import WorkOrder, WorkOrderStatus


def test_create_order_invalid_truck(client):
    http, _ = client
    resp = http.post(
        "/orders/",
        json={"truck_id": 999, "status_id": 999},
    )
    assert resp.status_code == 404


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
    assert resp.status_code == 404
