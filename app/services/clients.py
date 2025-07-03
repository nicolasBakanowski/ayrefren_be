from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.clients import ClientsRepository
from app.schemas.clients import ClientCreate


class ClientsService:
    def __init__(self, db: AsyncSession):
        self.repo = ClientsRepository(db)

    async def create_client(self, client_in: ClientCreate):
        return await self.repo.create(client_in)

    async def get_all_clients(self):
        return await self.repo.list_all()

    async def get_client_by_id(self, id: int):
        return await self.repo.get_by_id(id)

    async def delete_client(self, id: int):
        return await self.repo.delete(id)

    async def update_client(self, id: int, data: ClientCreate):
        return await self.repo.update(id, data)
