from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import validate_foreign_keys
from app.db.repositories.work_order_tasks import WorkOrderTasksRepository
from app.models.users import User
from app.models.work_orders import WorkOrder
from app.models.work_orders_mechanic import WorkArea
from app.schemas.work_order_tasks import WorkOrderTaskCreate, WorkOrderTaskUpdate


class WorkOrderTasksService:
    def __init__(self, db: AsyncSession):
        self.repo = WorkOrderTasksRepository(db)

    async def create_task(self, data: WorkOrderTaskCreate):
        await validate_foreign_keys(
            self.repo.db,
            {
                WorkOrder: data.work_order_id,
                User: data.user_id,
                WorkArea: data.area_id,
            },
        )
        return await self.repo.create(data)

    async def list_tasks(self, work_order_id: int):
        return await self.repo.list_by_work_order(work_order_id)

    async def update_task(self, task_id: int, data: WorkOrderTaskUpdate):
        await validate_foreign_keys(
            self.repo.db,
            {
                WorkOrder: data.work_order_id,
                User: data.user_id,
                WorkArea: data.area_id,
            },
        )
        updated = await self.repo.update(task_id, data.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        return updated

    async def delete_task(self, task_id: int):
        deleted = await self.repo.delete(task_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        return {"detail": "Tarea eliminada"}
