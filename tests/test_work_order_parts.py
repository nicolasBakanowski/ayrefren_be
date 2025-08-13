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


def test_part_flow(client):
    http, session_factory = client

    async def seed_data():
        async with session_factory() as session:
            from app.models.clients import Client, ClientType
            from app.models.trucks import Truck
            from app.models.work_orders import WorkOrder, WorkOrderStatus

            cli = Client(type=ClientType.persona, name="Owner")
            session.add(cli)
            await session.flush()
            truck = Truck(client_id=cli.id, license_plate="PART1")
            session.add(truck)
            status = WorkOrderStatus(name="open")
            session.add(status)
            await session.flush()
            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order.id

    order_id = asyncio.run(seed_data())
    resp = http.post(
        "/work-orders/parts/",
        json={
            "work_order_id": order_id,
            "quantity": 1,
            "name": "Part",
            "unit_price": 5,
            "subtotal": 5,
            "increment_per_unit": 0,
        },
    )
    assert resp.status_code == 200
    part_id = resp.json()["data"]["id"]

    resp = http.put(
        f"/work-orders/parts/{part_id}",
        json={"quantity": 2, "unit_price": 7, "subtotal": 14},
    )
    assert resp.status_code == 200
    updated = resp.json()["data"]
    assert updated["quantity"] == 2
    assert updated["unit_price"] == 7

    resp = http.get(f"/work-orders/parts/{order_id}")
    assert resp.status_code == 200
    parts = resp.json()["data"]
    assert next(p for p in parts if p["id"] == part_id)["quantity"] == 2

    resp = http.delete(f"/work-orders/parts/{part_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["detail"] == "Repuesto eliminado"

    resp = http.get(f"/work-orders/parts/{order_id}")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 0
