import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.db.repositories.clients import ClientsRepository
from app.schemas.clients import ClientCreate, ClientType

@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as db:
        yield db
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_and_get_client(session):
    repo = ClientsRepository(session)
    client_in = ClientCreate(type=ClientType.persona, name="John", document_number="123", phone="555")
    client = await repo.create(client_in)
    assert client.id is not None
    fetched = await repo.get_by_id(client.id)
    assert fetched is not None
    assert fetched.name == "John"

@pytest.mark.asyncio
async def test_delete_client(session):
    repo = ClientsRepository(session)
    client_in = ClientCreate(type=ClientType.persona, name="Jane")
    client = await repo.create(client_in)
    result = await repo.delete(client.id)
    assert result is True
    missing = await repo.get_by_id(client.id)
    assert missing is None

@pytest.mark.asyncio
async def test_update_client(session):
    repo = ClientsRepository(session)
    client_in = ClientCreate(type=ClientType.persona, name="Bob")
    client = await repo.create(client_in)
    update_data = ClientCreate(type=ClientType.empresa, name="Bob Corp", document_number="99")
    updated = await repo.update(client.id, update_data)
    assert updated is not None
    assert updated.type == ClientType.empresa
    assert updated.name == "Bob Corp"
    fetched = await repo.get_by_id(client.id)
    assert fetched.name == "Bob Corp"
