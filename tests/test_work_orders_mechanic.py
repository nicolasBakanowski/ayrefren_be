import asyncio


def test_assign_mechanic_invalid_fk(client):
    http, _ = client
    resp = http.post(
        "/work-orders/mechanics/",
        json={"work_order_id": 999, "user_id": 999, "area_id": 999},
    )
    assert resp.status_code == 404


def test_list_and_remove_mechanic(client):
    http, session_factory = client

    async def seed_data():
        async with session_factory() as session:
            from app.models.clients import Client, ClientType
            from app.models.trucks import Truck
            from app.models.users import Role, User
            from app.models.work_orders import WorkOrder, WorkOrderStatus
            from app.models.work_orders_mechanic import WorkArea

            role = Role(name="mech")
            area = WorkArea(name="area")
            cli = Client(type=ClientType.persona, name="Owner")
            session.add_all([role, area, cli])
            await session.flush()
            user = User(
                name="Mech", email="m@example.com", password="x", role_id=role.id
            )
            session.add(user)
            truck = Truck(client_id=cli.id, license_plate="MECH1")
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

    work_order_id, user_id, area_id = asyncio.run(seed_data())
    resp = http.post(
        "/work-orders/mechanics/",
        json={"work_order_id": work_order_id, "user_id": user_id, "area_id": area_id},
    )
    assert resp.status_code == 200
    mech_id = resp.json()["id"]

    resp = http.get(f"/work-orders/mechanics/{work_order_id}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = http.delete(f"/work-orders/mechanics/{mech_id}")
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Mecánico eliminado"
