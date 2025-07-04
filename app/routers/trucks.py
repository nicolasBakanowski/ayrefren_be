from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.schemas.trucks import TruckCreate, TruckInDB, TruckUpdate, TruckWithClient
from app.services.trucks import TrucksService

trucks_router = APIRouter()


@trucks_router.get("/", response_model=List[TruckInDB])
async def list_trucks(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    # Podés hacer paginación acá, filtro, etc.
    service = TrucksService(db)
    return await service.list_trucks()


@trucks_router.get("/{truck_id}", response_model=TruckInDB)
async def get_truck(
    truck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = TrucksService(db)
    return await service.get_truck(truck_id)


@trucks_router.get("/plate/{license_plate}", response_model=TruckWithClient)
async def get_truck_by_plate(
    license_plate: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = TrucksService(db)
    return await service.get_by_plate(license_plate)


@trucks_router.post("/", response_model=TruckInDB)
async def create_truck(
    truck_create: TruckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = TrucksService(db)
    return await service.create_truck(truck_create)


@trucks_router.put("/{truck_id}", response_model=TruckInDB)
async def update_truck(
    truck_id: int,
    truck_update: TruckUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = TrucksService(db)
    return await service.update_truck(truck_id, truck_update)


@trucks_router.delete("/{truck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_truck(
    truck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = TrucksService(db)
    await service.delete_truck(truck_id)
    return None
