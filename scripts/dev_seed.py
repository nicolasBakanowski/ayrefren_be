import asyncio
from datetime import date

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import engine
from app.models import (
    Client,
    ClientType,
    Expense,
    ExpenseType,
    Invoice,
    Payment,
    Role,
    Truck,
    User,
    WorkOrder,
    WorkOrderMechanic,
    WorkOrderPart,
    WorkOrderTask,
)
from scripts.init_db import init as init_basic_data

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_users(session: AsyncSession):
    roles = {
        "mechanic": "mechanic@example.com",
        "revisor": "revisor@example.com",
    }
    for role_name, email in roles.items():
        result = await session.execute(select(Role).where(Role.name == role_name))
        role = result.scalars().first()
        if not role:
            continue
        result = await session.execute(select(User).where(User.email == email))
        if not result.scalars().first():
            session.add(
                User(
                    name=role_name.capitalize(),
                    email=email,
                    password=pwd_context.hash(f"{role_name}123"),
                    role_id=role.id,
                    active=True,
                )
            )
    await session.commit()


async def seed_clients_and_trucks(session: AsyncSession):
    clients = [
        {
            "id": 1,
            "type": ClientType.persona,
            "name": "Juan Perez",
            "document_number": "11111111",
            "phone": "555-1111",
        },
        {
            "id": 2,
            "type": ClientType.empresa,
            "name": "ACME SA",
            "document_number": "30-12345678-9",
            "phone": "555-2222",
        },
    ]
    for data in clients:
        result = await session.execute(select(Client).where(Client.id == data["id"]))
        if not result.scalars().first():
            session.add(Client(**data))
    await session.commit()

    trucks = [
        {
            "id": 1,
            "client_id": 1,
            "license_plate": "AAA111",
            "brand": "Ford",
            "model": "F100",
        },
        {
            "id": 2,
            "client_id": 2,
            "license_plate": "BBB222",
            "brand": "Iveco",
            "model": "Stralis",
        },
    ]
    for data in trucks:
        result = await session.execute(select(Truck).where(Truck.id == data["id"]))
        if not result.scalars().first():
            session.add(Truck(**data))
    await session.commit()


async def seed_expenses(session: AsyncSession):
    if not await session.scalar(select(ExpenseType).where(ExpenseType.id == 1)):
        session.add(ExpenseType(id=1, name="Mantenimiento"))
    if not await session.scalar(select(Expense).where(Expense.id == 1)):
        session.add(
            Expense(
                id=1,
                date=date.today(),
                amount=100,
                description="Aceite",
                expense_type_id=1,
            )
        )
    await session.commit()


async def seed_work_orders(session: AsyncSession):
    mechanic_id = await session.scalar(
        select(User.id).where(User.email == "mechanic@example.com")
    )
    admin_id = await session.scalar(
        select(User.id).where(User.email == "admin@admin.com")
    )

    orders = [
        {
            "id": 1,
            "truck_id": 1,
            "status_id": 1,
            "reviewed_by": admin_id,
            "notes": "Revision general",
        },
        {
            "id": 2,
            "truck_id": 2,
            "status_id": 2,
            "reviewed_by": admin_id,
            "notes": "Cambio de aceite",
        },
    ]
    for data in orders:
        result = await session.execute(
            select(WorkOrder).where(WorkOrder.id == data["id"])
        )
        if not result.scalars().first():
            session.add(WorkOrder(**data))
    await session.commit()

    tasks = [
        {
            "id": 1,
            "work_order_id": 1,
            "user_id": mechanic_id or admin_id,
            "description": "Cambio de filtro",
            "area_id": 1,
            "price": 50.0,
            "external": False,
        },
        {
            "id": 2,
            "work_order_id": 2,
            "user_id": mechanic_id or admin_id,
            "description": "Alineacion",
            "area_id": 2,
            "price": 100.0,
            "external": False,
        },
    ]
    for data in tasks:
        result = await session.execute(
            select(WorkOrderTask).where(WorkOrderTask.id == data["id"])
        )
        if not result.scalars().first():
            session.add(WorkOrderTask(**data))
    await session.commit()

    parts = [
        {
            "id": 1,
            "work_order_id": 1,
            "part_id": 1,
            "quantity": 1,
            "unit_price": 80.0,
            "increment_per_unit": 1,
            "subtotal": 80.0,
        },
        {
            "id": 2,
            "work_order_id": 2,
            "part_id": 2,
            "quantity": 2,
            "unit_price": 40.0,
            "increment_per_unit": 1,
            "subtotal": 80.0,
        },
    ]
    for data in parts:
        result = await session.execute(
            select(WorkOrderPart).where(WorkOrderPart.id == data["id"])
        )
        if not result.scalars().first():
            session.add(WorkOrderPart(**data))
    await session.commit()

    mechanics = [
        {
            "id": 1,
            "work_order_id": 1,
            "user_id": mechanic_id or admin_id or None,
            "area_id": 1,
            "notes": "Inicio",
        },
        {
            "id": 2,
            "work_order_id": 2,
            "user_id": mechanic_id or admin_id or None,
            "area_id": 2,
            "notes": "Inicio",
        },
    ]
    for data in mechanics:
        result = await session.execute(
            select(WorkOrderMechanic).where(WorkOrderMechanic.id == data["id"])
        )
        if not result.scalars().first():
            session.add(WorkOrderMechanic(**data))
    await session.commit()


async def seed_invoices(session: AsyncSession):
    invoices = [
        {
            "id": 1,
            "work_order_id": 1,
            "client_id": 1,
            "invoice_type_id": 1,
            "status_id": 1,
            "labor_total": 50.0,
            "parts_total": 80.0,
            "iva": 21.0,
            "total": 151.0,
        },
        {
            "id": 2,
            "work_order_id": 2,
            "client_id": 2,
            "invoice_type_id": 2,
            "status_id": 1,
            "labor_total": 100.0,
            "parts_total": 80.0,
            "iva": 21.0,
            "total": 201.0,
        },
    ]
    for data in invoices:
        result = await session.execute(select(Invoice).where(Invoice.id == data["id"]))
        if not result.scalars().first():
            session.add(Invoice(**data))
    await session.commit()

    payments = [
        {"id": 1, "invoice_id": 1, "method_id": 1, "amount": 151.0},
        {"id": 2, "invoice_id": 2, "method_id": 2, "amount": 201.0},
    ]
    for data in payments:
        result = await session.execute(select(Payment).where(Payment.id == data["id"]))
        if not result.scalars().first():
            session.add(Payment(**data))
    await session.commit()


async def seed():
    await init_basic_data()
    async with AsyncSession(engine) as session:
        await seed_users(session)
        await seed_clients_and_trucks(session)
        await seed_expenses(session)
        await seed_work_orders(session)
        await seed_invoices(session)


if __name__ == "__main__":
    asyncio.run(seed())
