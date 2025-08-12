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
    task_id = resp.json()["data"]["id"]

    resp = http.get(f"/work-orders/tasks/{order_id}")
    assert resp.status_code == 200
    assert any(t["id"] == task_id for t in resp.json()["data"])

    resp = http.delete(f"/work-orders/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["detail"] == "Tarea eliminada"

    resp = http.get(f"/work-orders/tasks/{order_id}")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 0


def test_earnings_and_mark_paid(client):
    from datetime import datetime

    http, session_factory = client

    async def seed():
        async with session_factory() as session:
            from app.models.clients import Client, ClientType
            from app.models.trucks import Truck
            from app.models.users import Role, User
            from app.models.work_orders import WorkOrder, WorkOrderStatus
            from app.models.work_orders_mechanic import WorkArea
            from app.models.work_order_tasks import WorkOrderTask

            role = Role(name="role2")
            area = WorkArea(id=1, name="area1")
            cli = Client(type=ClientType.persona, name="Owner2")
            session.add_all([role, area, cli])
            await session.flush()
            user = User(name="Worker2", email="w2@example.com", password="x", role_id=role.id)
            session.add(user)
            truck = Truck(client_id=cli.id, license_plate="EARN1")
            session.add(truck)
            status_final = WorkOrderStatus(id=3, name="final")
            status_other = WorkOrderStatus(id=2, name="other")
            session.add_all([status_final, status_other])
            await session.flush()
            wo_final = WorkOrder(truck_id=truck.id, status_id=status_final.id)
            wo_other = WorkOrder(truck_id=truck.id, status_id=status_other.id)
            session.add_all([wo_final, wo_other])
            await session.flush()
            t1 = WorkOrderTask(
                work_order_id=wo_final.id,
                user_id=user.id,
                description="t1",
                area_id=area.id,
                price=100,
                external=False,
                created_at=datetime(2023, 1, 1),
            )
            t2 = WorkOrderTask(
                work_order_id=wo_final.id,
                user_id=user.id,
                description="t2",
                area_id=area.id,
                price=200,
                external=False,
                paid=True,
                paid_at=datetime(2023, 1, 2),
                created_at=datetime(2023, 1, 2),
            )
            t3 = WorkOrderTask(
                work_order_id=wo_other.id,
                user_id=user.id,
                description="t3",
                area_id=area.id,
                price=150,
                external=False,
                created_at=datetime(2023, 1, 3),
            )
            session.add_all([t1, t2, t3])
            await session.commit()
            await session.refresh(t1)
            return t1.id

    task_id = asyncio.run(seed())

    resp = http.get("/work-orders/tasks/earnings")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["summary"]["total_amount"] == 100
    assert data["summary"]["count"] == 1

    resp = http.post(
        "/work-orders/tasks/mark-paid", json={"task_ids": [task_id]}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["updated"] == 1

    resp = http.get("/work-orders/tasks/earnings")
    assert resp.status_code == 200
    assert resp.json()["data"]["summary"]["count"] == 0

    resp = http.get(
        "/work-orders/tasks/earnings", params={"from": "2023-02-01", "to": "2023-01-01"}
    )
    assert resp.json()["code"] == 400
