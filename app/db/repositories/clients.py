from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from sqlalchemy import and_
from app.models.clients import Client
from app.schemas.clients import ClientCreate


class ClientsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, client_in: ClientCreate) -> Client:
        db_client = Client(**client_in.model_dump())
        self.db.add(db_client)
        await self.db.commit()
        await self.db.refresh(db_client)
        return db_client

    async def list_all(
        self,
        type: Optional[str] = None,
        name: Optional[str] = None,
        document_number: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> list[Client]:
        query = select(Client)

        filters = []
        if type:
            filters.append(Client.type == type)
        if name:
            filters.append(Client.name.ilike(f"%{name}%"))
        if document_number:
            filters.append(Client.document_number == document_number)
        if phone:
            filters.append(Client.phone == phone)

        if filters:
            query = query.where(and_(*filters))

        result = await self.db.execute(query)
        return result.scalars().all()
    async def get_by_id(self, client_id: int) -> Client | None:
        result = await self.db.execute(select(Client).where(Client.id == client_id))
        return result.scalar_one_or_none()

    async def delete(self, client_id: int) -> bool:
        result = await self.db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        if client is None:
            return False
        await self.db.delete(client)
        await self.db.commit()
        return True

    async def update(self, client_id: int, data: ClientCreate) -> Client | None:
        result = await self.db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        if client is None:
            return None
        for key, value in data.items():
            setattr(client, key, value)
        await self.db.commit()
        await self.db.refresh(client)
        return client
