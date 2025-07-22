from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, MECHANIC, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.core.responses import success_response
from app.schemas.response import ResponseSchema
from app.schemas.work_orders_mechanic import (
    WorkOrderMechanicCreate,
    WorkOrderMechanicOut,
)
from app.services.work_orders_mechanic import WorkOrdersMechanicService

work_orders_mechanic_router = APIRouter()


@work_orders_mechanic_router.post(
    "/", response_model=ResponseSchema[WorkOrderMechanicOut]
)
async def assign_mechanic(
    mechanic_in: WorkOrderMechanicCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrdersMechanicService(db)
    data = await service.assign_mechanic(mechanic_in)
    return success_response(data=data)


@work_orders_mechanic_router.get(
    "/{work_order_id}", response_model=ResponseSchema[list[WorkOrderMechanicOut]]
)
async def list_mechanics(
    work_order_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrdersMechanicService(db)
    data = await service.list_mechanics(work_order_id)
    return success_response(data=data)


@work_orders_mechanic_router.delete("/{mechanic_id}")
async def remove_mechanic(
    mechanic_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrdersMechanicService(db)
    data = await service.remove_mechanic(mechanic_id)
    return success_response(data=data)
