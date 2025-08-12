import asyncio
import os
import tempfile
from datetime import datetime

from alembic import command
from alembic.config import Config
from app.models.clients import Client, ClientType
from app.models.trucks import Truck
from app.models.users import Role, User
from app.models.work_orders import WorkOrder, WorkOrderStatus
from app.models.work_order_tasks import WorkOrderTask
from app.models.work_orders_mechanic import WorkArea


def test_migration_upgrade_and_downgrade():
    cfg = Config("alembic.ini")
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
        command.upgrade(cfg, "head")
        command.downgrade(cfg, "base")


def test_summary_no_tasks(client):
    http, _ = client
    resp = http.get(
        "/work-orders/tasks/summary",
        params={"date_from": "2025-01-01", "date_to": "2025-01-31", "work_area_id": 1},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["count"] == 0
    assert data["total_amount"] == 0


def test_summary_and_mark_paid(client):
    http, session_factory = client

    async def seed_data():
        async with session_factory() as session:
            role = Role(name="tasker")
            area = WorkArea(name="area")
            cli = Client(type=ClientType.persona, name="Owner")
            session.add_all([role, area, cli])
            await session.flush()
            user = User(
                name="Worker", email="w@example.com", password="x", role_id=role.id
            )
            session.add(user)
            truck = Truck(client_id=cli.id, license_plate="TASK2")
            session.add(truck)
            status = WorkOrderStatus(name="open")
            session.add(status)
            await session.flush()
            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            session.add(order)
            await session.flush()
            t1 = WorkOrderTask(
                work_order_id=order.id,
                user_id=user.id,
                area_id=area.id,
                description="t1",
                price=10,
                created_at=datetime(2025, 8, 1, 10, 0, 0),
            )
            t2 = WorkOrderTask(
                work_order_id=order.id,
                user_id=user.id,
                area_id=area.id,
                description="t2",
                price=20,
                created_at=datetime(2025, 8, 2, 12, 0, 0),
            )
            session.add_all([t1, t2])
            await session.commit()
            await session.refresh(t1)
            await session.refresh(t2)
            return area.id, [t1.id, t2.id]

    area_id, task_ids = asyncio.run(seed_data())

    resp = http.get(
        "/work-orders/tasks/summary",
        params={
            "work_area_id": area_id,
            "date_from": "2025-08-01",
            "date_to": "2025-08-03",
        },
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["count"] == 2
    assert data["total_amount"] == 30.0

    resp = http.post(
        "/work-orders/tasks/mark-paid",
        json={"task_ids": task_ids, "paid_at": "2025-08-12T00:00:00Z"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["updated"] == 2

    resp = http.get(
        "/work-orders/tasks/summary",
        params={
            "work_area_id": area_id,
            "date_from": "2025-08-01",
            "date_to": "2025-08-03",
        },
    )
    data = resp.json()["data"]
    assert data["count"] == 0
    assert data["total_amount"] == 0
