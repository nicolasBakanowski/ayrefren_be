from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.repositories.clients import ClientsRepository
from app.schemas.clients import ClientCreate
from fastapi import HTTPException, status


class ClientsService:
    def __init__(self, db: AsyncSession):
        self.repo = ClientsRepository(db)

    async def create_client(self, client_in: ClientCreate):
        return await self.repo.create(client_in)

    async def get_all_clients(
        self,
        type: Optional[str] = None,
        name: Optional[str] = None,
        document_number: Optional[str] = None,
        phone: Optional[str] = None,
    ):
        clients = await self.repo.list_all(
            type=type,
            name=name,
            document_number=document_number,
            phone=phone,
        )
        if not clients:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Client Found")
        return clients

    async def get_client_by_id(self, id: int):
        return await self.repo.get_by_id(id)

    async def delete_client(self, id: int):
        return await self.repo.delete(id)

    async def update_client(self, id: int, data: ClientCreate):
        return await self.repo.update(id, data)
