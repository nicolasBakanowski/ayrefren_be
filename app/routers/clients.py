from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.responses import success_response
from app.schemas.clients import ClientCreate, ClientOut
from app.schemas.response import ResponseSchema
from app.services.clients import ClientsService

clients_router = APIRouter()


@clients_router.get("/", response_model=ResponseSchema[list[ClientOut]])
async def list_clients(
    type: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    document_number: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = ClientsService(db)
    data = await service.get_all_clients(
        type=type,
        name=name,
        document_number=document_number,
        phone=phone,
    )
    return success_response(data=data)


@clients_router.post("/")
async def create_client(client_in: ClientCreate, db: AsyncSession = Depends(get_db)):
    service = ClientsService(db)
    data = await service.create_client(client_in)
    return success_response(data=data)


@clients_router.get("/{id}", response_model=ResponseSchema[ClientOut])
async def get_client(id: int, db: AsyncSession = Depends(get_db)):
    service = ClientsService(db)
    data = await service.get_client_by_id(id)
    return success_response(data=data)


@clients_router.delete("/{id}")
async def delete_client(id: int, db: AsyncSession = Depends(get_db)):
    service = ClientsService(db)
    data = await service.delete_client(id)
    return success_response(data=data)


@clients_router.put("/{id}")
async def update_client(
    id: int, client_in: ClientOut, db: AsyncSession = Depends(get_db)
):
    service = ClientsService(db)
    data = await service.update_client(id, client_in)
    return success_response(data=data)
