from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.work_order_tasks import WorkOrderTasksRepository
from app.schemas.work_order_tasks import WorkOrderTaskCreate


class WorkOrderTasksService:
    def __init__(self, db: AsyncSession):
        self.repo = WorkOrderTasksRepository(db)

    async def create_task(self, data: WorkOrderTaskCreate):
        return await self.repo.create(data)

    async def list_tasks(self, work_order_id: int):
        return await self.repo.list_by_work_order(work_order_id)

    async def delete_task(self, task_id: int):
        deleted = await self.repo.delete(task_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        return {"detail": "Tarea eliminada"}
