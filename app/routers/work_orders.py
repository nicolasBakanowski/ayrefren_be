from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, MECHANIC, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.core.responses import success_response
from app.schemas.work_orders import WorkOrderCreate, WorkOrderOut, WorkOrderUpdate
from app.schemas.response import ResponseSchema
from app.services.work_orders import WorkOrdersService

work_orders_router = APIRouter()


@work_orders_router.post("/")
async def create_order(
    data: WorkOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = WorkOrdersService(db)
    work_order = await service.create_work_order(data)
    return success_response(data=work_order)


@work_orders_router.get("/", response_model=ResponseSchema[list[WorkOrderOut]])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrdersService(db)
    orders = await service.list_work_orders()
    return success_response(data=orders)


@work_orders_router.get("/{order_id}/total", response_model=ResponseSchema[dict])
async def order_total(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrdersService(db)
    total = await service.calculate_total(order_id)
    return success_response(data={"total": total})


@work_orders_router.get("/{order_id}", response_model=ResponseSchema[WorkOrderOut])
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrdersService(db)
    order = await service.get_work_order(order_id)
    return success_response(data=order)


@work_orders_router.put("/{order_id}")
async def update_order(
    order_id: int,
    data: WorkOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = WorkOrdersService(db)
    data = await service.update_work_order(order_id, data)
    return success_response(data=data)


@work_orders_router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrdersService(db)
    data = await service.delete_work_order(order_id)
    return success_response(data=data)
