from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.schemas.parts import PartCreate, PartOut, PartUpdate
from app.core.responses import success_response
from app.services.parts import PartsService

parts_router = APIRouter()


@parts_router.get("/", response_model=list[PartOut])
async def list_parts(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PartsService(db)
    return await service.list_parts()


@parts_router.get("/{part_id}", response_model=PartOut)
async def get_part(
    part_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PartsService(db)
    return await service.get_part(part_id)


@parts_router.post("/")
async def create_part(
    part_in: PartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PartsService(db)
    data = await service.create_part(part_in)
    return success_response(data=data)


@parts_router.put("/{part_id}")
async def update_part(
    part_update: PartUpdate,
    part_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = PartsService(db)
    data = await service.update_part(part_id, part_update)
    return success_response(data=data)


@parts_router.delete("/{part_id}")
async def delete_part(
    part_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = PartsService(db)
    data = await service.delete_part(part_id)
    return success_response(data=data)
