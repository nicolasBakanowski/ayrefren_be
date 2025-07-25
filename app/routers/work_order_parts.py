from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, MECHANIC, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.core.responses import success_response
from app.schemas.response import ResponseSchema
from app.schemas.work_order_parts import WorkOrderPartCreate, WorkOrderPartOut
from app.services.work_order_parts import WorkOrderPartsService

work_order_parts_router = APIRouter()


@work_order_parts_router.get("/names", response_model=ResponseSchema[list[str]])
async def list_names(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrderPartsService(db)
    data = await service.list_names()
    return success_response(data=data)


@work_order_parts_router.post("/", response_model=ResponseSchema[WorkOrderPartOut])
async def add_part(
    part_in: WorkOrderPartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrderPartsService(db)
    data = await service.create_part(part_in)
    return success_response(data=data)


@work_order_parts_router.get(
    "/{work_order_id}", response_model=ResponseSchema[list[WorkOrderPartOut]]
)
async def list_parts(
    work_order_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrderPartsService(db)
    data = await service.list_parts(work_order_id)
    return success_response(data=data)


@work_order_parts_router.delete("/{part_id}")
async def remove_part(
    part_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrderPartsService(db)
    data = await service.delete_part(part_id)
    return success_response(data=data)
