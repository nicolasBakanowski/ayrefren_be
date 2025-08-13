from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import validate_foreign_keys
from app.db.repositories.work_order_tasks import WorkOrderTasksRepository
from app.models.users import User
from app.models.work_orders import WorkOrder
from app.models.work_orders_mechanic import WorkArea
from app.models.invoices import Invoice
from app.schemas.work_order_tasks import WorkOrderTaskCreate, WorkOrderTaskUpdate


class WorkOrderTasksService:
    def __init__(self, db: AsyncSession):
        self.repo = WorkOrderTasksRepository(db)

    async def _ensure_editable(self, work_order_id: int):
        result = await self.repo.db.execute(
            select(Invoice.id).where(Invoice.work_order_id == work_order_id)
        )
        if result.first():
            raise HTTPException(
                status_code=400, detail="La orden ya está facturada"
            )

    async def create_task(self, data: WorkOrderTaskCreate):
        await validate_foreign_keys(
            self.repo.db,
            {
                WorkOrder: data.work_order_id,
                User: data.user_id,
                WorkArea: data.area_id,
            },
        )
        await self._ensure_editable(data.work_order_id)
        return await self.repo.create(data)

    async def list_tasks(self, work_order_id: int):
        return await self.repo.list_by_work_order(work_order_id)

    async def update_task(self, task_id: int, data: WorkOrderTaskUpdate):
        task = await self.repo.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        await self._ensure_editable(task.work_order_id)
        if data.work_order_id and data.work_order_id != task.work_order_id:
            await validate_foreign_keys(self.repo.db, {WorkOrder: data.work_order_id})
            await self._ensure_editable(data.work_order_id)
        await validate_foreign_keys(
            self.repo.db,
            {
                User: data.user_id,
                WorkArea: data.area_id,
            },
        )
        updated = await self.repo.update(task_id, data.dict(exclude_unset=True))
        return updated

    async def delete_task(self, task_id: int):
        task = await self.repo.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        await self._ensure_editable(task.work_order_id)
        deleted = await self.repo.delete(task_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        return {"detail": "Tarea eliminada"}
