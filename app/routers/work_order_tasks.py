from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, MECHANIC, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.core.responses import success_response
from app.schemas.response import ResponseSchema
from app.schemas.work_order_tasks import (
    MarkPaidIn,
    MarkPaidOut,
    TasksResponse,
    WorkOrderTaskCreate,
    WorkOrderTaskOut,
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


@work_order_tasks_router.get(
    "/earnings", response_model=ResponseSchema[TasksResponse]
)
async def get_earnings(
    area_id: int = Query(1, gt=0),
    from_: str | None = Query(None, alias="from"),
    to: str | None = Query(None),
    paid: bool | None = Query(False),
    only_finalized: bool = Query(True),
    external: bool | None = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    def _parse_dt(value: str | None) -> datetime | None:
        if value is None:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Invalid datetime format") from exc

    from_dt = _parse_dt(from_)
    to_dt = _parse_dt(to)

    service = WorkOrderTasksService(db)
    data = await service.get_earnings(
        area_id, paid, from_dt, to_dt, only_finalized, external
    )
    return success_response(data=data)


@work_order_tasks_router.post(
    "/mark-paid", response_model=ResponseSchema[MarkPaidOut]
)
async def mark_paid(
    body: MarkPaidIn,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrderTasksService(db)
    data = await service.mark_paid(body)
    return success_response(data=data)
