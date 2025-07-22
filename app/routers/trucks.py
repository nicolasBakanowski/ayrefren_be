from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.core.responses import success_response
from app.schemas.response import ResponseSchema
from app.schemas.trucks import TruckCreate, TruckInDB, TruckUpdate
from app.services.trucks import TrucksService

trucks_router = APIRouter()


@trucks_router.get("/", response_model=ResponseSchema[list[TruckInDB]])
async def list_trucks(
    client_id: int = None,
    license_plate: str = None,
    brand: str = None,
    model: str = None,
    year: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    # Podés hacer paginación acá, filtro, etc.
    service = TrucksService(db)
    data = await service.list_trucks(
        client_id=client_id,
        license_plate=license_plate,
        brand=brand,
        model=model,
        year=year,
    )
    return success_response(data=data)


@trucks_router.get("/{truck_id}", response_model=ResponseSchema[TruckInDB])
async def get_truck(
    truck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = TrucksService(db)
    data = await service.get_truck(truck_id)
    return success_response(data=data)


@trucks_router.post("/", response_model=ResponseSchema[TruckInDB])
async def create_truck(
    truck_create: TruckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = TrucksService(db)
    data = await service.create_truck(truck_create)
    return success_response(data=data)


@trucks_router.put("/{truck_id}")
async def update_truck(
    truck_id: int,
    truck_update: TruckUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = TrucksService(db)
    data = await service.update_truck(truck_id, truck_update)
    return success_response(data=data)


@trucks_router.delete("/{truck_id}")
async def delete_truck(
    truck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = TrucksService(db)
    await service.delete_truck(truck_id)
    return success_response()
