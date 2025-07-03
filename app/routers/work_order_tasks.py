from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, MECHANIC, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.schemas.work_order_tasks import WorkOrderTaskCreate, WorkOrderTaskOut
from app.services.work_order_tasks import WorkOrderTasksService

work_order_tasks_router = APIRouter()


@work_order_tasks_router.post("/", response_model=WorkOrderTaskOut)
async def create_task(
    task_in: WorkOrderTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrderTasksService(db)
    return await service.create_task(task_in)


@work_order_tasks_router.get("/{work_order_id}", response_model=list[WorkOrderTaskOut])
async def list_tasks(
    work_order_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN, REVISOR, MECHANIC)),
):
    service = WorkOrderTasksService(db)
    return await service.list_tasks(work_order_id)


@work_order_tasks_router.delete(
    "/{task_id}",
)
async def delete_task(
    task_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrderTasksService(db)
    return await service.delete_task(task_id)
