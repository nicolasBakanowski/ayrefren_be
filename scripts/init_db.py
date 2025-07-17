# scripts/init_db.py

import asyncio

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import engine
from app.models import InvoiceStatus, PaymentMethod
from app.models.invoices import InvoiceType
from app.models.parts import Part
from app.models.users import (  # Asegurate que los modelos estén bien importados
    Role,
    User,
)
from app.models.work_orders import WorkOrderStatus
from app.models.work_orders_mechanic import WorkArea

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_data(data, session, model):
    # PARA TODOS LOS MODELOS CON CAMPOS "id" y "name"
    for key, value in data.items():
        result = await session.execute(select(model).where(model.id == key))
        existing_status = result.scalars().first()
        if not existing_status:
            session.add(model(id=key, name=value))
    await session.commit()


async def init():
    async with AsyncSession(engine) as session:
        # Insertar los roles de usuario
        roles = {
            "admin": "Administrador del sistema",
            "mechanic": "Mecánico",
            "revisor": "Gerente",
            "client": "Cliente",
        }

        for name, desc in roles.items():
            result = await session.execute(select(Role).where(Role.name == name))
            existing_role = result.scalars().first()

            if not existing_role:
                session.add(Role(name=name, description=desc))

        await session.commit()

        # Insertar los estados de las órdenes de trabajo
        statuses = {
            1: "Pendiente",
            2: "En progreso",
            3: "Finalizado",
            4: "Emitido"
        }
        await create_data(statuses, session, WorkOrderStatus)

        # Insertar tipos de facturas
        invoice_types = {
            1: "Factura A",
            2: "Factura C",
            3: "Remito",
        }
        await create_data(invoice_types, session, InvoiceType)

        # Insertar estados de las facturas
        invoice_statuses = {
            1: "Pendiente",
            2: "Pagada",
            3: "Anulada",
            4: "Entrega Parcial",
        }
        await create_data(invoice_statuses, session, InvoiceStatus)

        # Insertar moteodos de pago
        payment_methods = {
            1: "Efectivo",
            2: "Tarjeta de crédito",
            3: "Tarjeta de débito",
            4: "Transferencia bancaria",
            5: "Cheque",  # AQUI TENEMOS DOS TIPOS ELECTRONICOS Y FISICOS
        }
        await create_data(payment_methods, session, PaymentMethod)

        # Work Areas
        work_areas = {
            1: "Mecánica Aire",
            2: "Mecánica general",
        }
        await create_data(work_areas, session, WorkArea)

        # Sample Parts
        sample_parts = [
            {"id": 1, "name": "Filtro de aceite", "price": 80.0},
            {"id": 2, "name": "Bujía", "price": 40.0},
        ]
        for part in sample_parts:
            result = await session.execute(select(Part).where(Part.id == part["id"]))
            existing = result.scalars().first()
            if not existing:
                session.add(Part(**part))
        await session.commit()

        # Obtener el rol "admin" ya insertado
        result = await session.execute(select(Role).where(Role.name == "admin"))
        admin_role = result.scalars().first()
        if admin_role:
            result = await session.execute(
                select(User).where(User.email == "admin@admin.com")
            )
            existing_user = result.scalars().first()

            if not existing_user:
                hashed_password = pwd_context.hash("admin123")
                admin_user = User(
                    name="Admin",
                    email="admin@admin.com",
                    password=hashed_password,
                    role_id=admin_role.id,
                    active=True,
                )
                session.add(admin_user)
                await session.commit()


if __name__ == "__main__":
    asyncio.run(init())
