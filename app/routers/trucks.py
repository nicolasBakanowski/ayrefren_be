from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.schemas.trucks import TruckCreate, TruckInDB, TruckUpdate
from app.services.trucks import TrucksService

trucks_router = APIRouter()


@trucks_router.get("/", response_model=List[TruckInDB], dependencies=[Depends(roles_allowed("admin", "revisor"))])
async def list_trucks(db: AsyncSession = Depends(get_db)):
    # Podés hacer paginación acá, filtro, etc.
    service = TrucksService(db)
    return await service.list_trucks()


@trucks_router.get("/{truck_id}", response_model=TruckInDB, dependencies=[Depends(roles_allowed("admin", "revisor"))])
async def get_truck(truck_id: int, db: AsyncSession = Depends(get_db)):
    service = TrucksService(db)
    return await service.get_truck(truck_id)


@trucks_router.post("/", response_model=TruckInDB, dependencies=[Depends(roles_allowed("admin", "revisor"))])
async def create_truck(truck_create: TruckCreate, db: AsyncSession = Depends(get_db)):
    service = TrucksService(db)
    return await service.create_truck(truck_create)


@trucks_router.put("/{truck_id}", response_model=TruckInDB, dependencies=[Depends(roles_allowed("admin", "revisor"))])
async def update_truck(truck_id: int, truck_update: TruckUpdate, db: AsyncSession = Depends(get_db)):
    service = TrucksService(db)
    return await service.update_truck(truck_id, truck_update)


@trucks_router.delete("/{truck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_truck(truck_id: int, db: AsyncSession = Depends(get_db)):
    service = TrucksService(db)
    await service.delete_truck(truck_id)
    return None
