import asyncio

def test_add_task_invalid_fk(client):
    http, _ = client
    resp = http.post(
        "/work-orders/tasks/",
        json={
            "work_order_id": 999,
            "user_id": 999,
            "area_id": 999,
            "description": "",
            "price": 0,
            "external": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]
    assert data["code"] == 404


def test_task_flow(client):
    http, session_factory = client

    async def seed_data():
        async with session_factory() as session:
            from app.models.clients import Client, ClientType
            from app.models.trucks import Truck
            from app.models.users import Role, User
            from app.models.work_orders import WorkOrder, WorkOrderStatus
            from app.models.work_orders_mechanic import WorkArea

            role = Role(name="tasker")
            area = WorkArea(name="area")
            cli = Client(type=ClientType.persona, name="Owner")
            session.add_all([role, area, cli])
            await session.flush()
            user = User(
                name="Worker", email="w@example.com", password="x", role_id=role.id
            )
            session.add(user)
            truck = Truck(client_id=cli.id, license_plate="TASK1")
            session.add(truck)
            status = WorkOrderStatus(name="open")
            session.add(status)
            await session.flush()
            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.commit()
            await session.refresh(order)
            await session.refresh(user)
            await session.refresh(area)
            return order.id, user.id, area.id

    order_id, user_id, area_id = asyncio.run(seed_data())
    resp = http.post(
        "/work-orders/tasks/",
        json={
            "work_order_id": order_id,
            "user_id": user_id,
            "area_id": area_id,
            "description": "Fix",
            "price": 10.0,
            "external": True,
        },
    )
    assert resp.status_code == 200
    task_data = resp.json()["data"]
    task_id = task_data["id"]
    assert task_data["paid"] is False

    resp = http.get(f"/work-orders/tasks/{order_id}")
    assert resp.status_code == 200
    tasks = resp.json()["data"]
    assert any(t["id"] == task_id for t in tasks)
    assert next(t for t in tasks if t["id"] == task_id)["paid"] is False

    resp = http.put(
        f"/work-orders/tasks/{task_id}",
        json={"price": 15.0, "paid": True},
    )
    assert resp.status_code == 200
    updated = resp.json()["data"]
    assert updated["price"] == 15.0
    assert updated["paid"] is True

    resp = http.get(f"/work-orders/tasks/{order_id}")
    assert resp.status_code == 200
    tasks = resp.json()["data"]
    assert next(t for t in tasks if t["id"] == task_id)["paid"] is True

    resp = http.delete(f"/work-orders/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["detail"] == "Tarea eliminada"

    resp = http.get(f"/work-orders/tasks/{order_id}")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 0
