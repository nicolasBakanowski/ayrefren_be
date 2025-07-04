# scripts/init_db.py

import asyncio

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import engine
from app.models.users import (  # Asegurate que los modelos estén bien importados
    Role,
    User,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init():
    async with AsyncSession(engine) as session:
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
