from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import validate_foreign_keys
from app.db.repositories.work_order_tasks import WorkOrderTasksRepository
from app.models.users import User
from app.models.work_orders import WorkOrder
from app.models.work_orders_mechanic import WorkArea
from app.schemas.work_order_tasks import (
    WorkOrderTaskCreate,
    WorkOrderTaskMarkPaid,
    WorkOrderTasksSummaryOut,
)


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

    async def delete_task(self, task_id: int):
        deleted = await self.repo.delete(task_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        return {"detail": "Tarea eliminada"}

    async def summary(
        self,
        work_area_id: int,
        date_from: date,
        date_to: date,
        paid: bool,
    ) -> WorkOrderTasksSummaryOut:
        date_from_dt = datetime.combine(date_from, datetime.min.time())
        date_to_dt = datetime.combine(date_to, datetime.max.time())
        tasks, count, total = await self.repo.summary(
            work_area_id, date_from_dt, date_to_dt, paid
        )
        return WorkOrderTasksSummaryOut(
            work_area_id=work_area_id,
            date_from=date_from,
            date_to=date_to,
            paid=paid,
            count=count,
            total_amount=total,
            tasks=tasks,
        )

    async def mark_paid(self, data: WorkOrderTaskMarkPaid) -> dict:
        paid_at = data.paid_at or datetime.utcnow()
        updated = await self.repo.mark_paid(data.task_ids, paid_at)
        return {"updated": updated}
