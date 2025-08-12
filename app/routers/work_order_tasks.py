from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, MECHANIC, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.core.responses import success_response
from app.schemas.response import ResponseSchema
from app.schemas.work_order_tasks import (
    WorkOrderTaskCreate,
    WorkOrderTaskMarkPaid,
    WorkOrderTaskOut,
    WorkOrderTasksSummaryOut,
)
from app.services.work_order_tasks import WorkOrderTasksService

work_order_tasks_router = APIRouter()


@work_order_tasks_router.post("/", response_model=ResponseSchema[WorkOrderTaskOut])
async def create_task(
    task_in: WorkOrderTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrderTasksService(db)
    data = await service.create_task(task_in)
    return success_response(data=data)


@work_order_tasks_router.get(
    "/summary", response_model=ResponseSchema[WorkOrderTasksSummaryOut]
)
async def summary_tasks(
    date_from: date = Query(...),
    date_to: date = Query(...),
    work_area_id: int = Query(1),
    paid: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR)),
):
    if date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be <= date_to")
    service = WorkOrderTasksService(db)
    data = await service.summary(work_area_id, date_from, date_to, paid)
    return success_response(data=data)


@work_order_tasks_router.post(
    "/mark-paid", response_model=ResponseSchema[dict]
)
async def mark_paid(
    payload: WorkOrderTaskMarkPaid,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrderTasksService(db)
    data = await service.mark_paid(payload)
    return success_response(data=data)


@work_order_tasks_router.get(
    "/{work_order_id}", response_model=ResponseSchema[list[WorkOrderTaskOut]]
)
async def list_tasks(
    work_order_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrderTasksService(db)
    data = await service.list_tasks(work_order_id)
    return success_response(data=data)


@work_order_tasks_router.delete(
    "/{task_id}",
)
async def delete_task(
    task_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrderTasksService(db)
    data = await service.delete_task(task_id)
    return success_response(data=data)
