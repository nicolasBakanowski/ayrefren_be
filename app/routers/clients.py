from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.clients import ClientOut
from app.services.clients import ClientsService

clients_router = APIRouter()


@clients_router.get("/", response_model=list[ClientOut])
async def list_clients(db: AsyncSession = Depends(get_db)):
    service = ClientsService(db)
    return await service.get_all_clients()


@clients_router.post("/", response_model=ClientOut)
async def create_client(client_in: ClientOut, db: AsyncSession = Depends(get_db)):
    service = ClientsService(db)
    return await service.create_client(client_in)


@clients_router.get("/{id}", response_model=ClientOut)
async def get_client(id: int, db: AsyncSession = Depends(get_db)):
    service = ClientsService(db)
    return await service.get_client_by_id(id)


@clients_router.delete("/{id}", response_model=bool)
async def delete_client(id: int, db: AsyncSession = Depends(get_db)):
    service = ClientsService(db)
    return await service.delete_client(id)


@clients_router.put("/{id}", response_model=ClientOut)
async def update_client(
    id: int, client_in: ClientOut, db: AsyncSession = Depends(get_db)
):
    service = ClientsService(db)
    return await service.update_client(id, client_in)
