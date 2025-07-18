import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.dependencies import get_current_user
from app.core.database import Base, get_db
from app.models.users import Role, User
from app.main import app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="function")
def client():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with async_session() as session:
            yield session

    def override_get_current_user():
        return User(
            id=1,
            name="Test",
            email="test@example.com",
            password="x",
            role_id=1,
            active=True,
            role=Role(id=1, name="admin"),
        )

    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create_tables())

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as ac:
        yield ac, async_session
    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())
