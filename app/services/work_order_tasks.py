from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import validate_foreign_keys
from app.db.repositories.work_order_tasks import WorkOrderTasksRepository
from app.models.users import User
from app.models.work_orders import WorkOrder
from app.models.work_orders_mechanic import WorkArea
from app.schemas.work_order_tasks import (
    MarkPaidIn,
    MarkPaidOut,
    TasksFilterOut,
    TasksResponse,
    TasksSummaryOut,
    WorkOrderTaskCreate,
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

    async def get_earnings(
        self,
        area_id: int = 1,
        paid: bool | None = False,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
        only_finalized: bool = True,
        external: bool | None = False,
    ) -> TasksResponse:
        if from_dt and to_dt and from_dt > to_dt:
            raise HTTPException(status_code=400, detail="Rango de fechas inválido")

        items = await self.repo.list_tasks_filtered(
            area_id,
            paid,
            from_dt,
            to_dt,
            only_finalized,
            external,
        )
        summary_data = await self.repo.aggregate_tasks(
            area_id, paid, from_dt, to_dt, only_finalized, external
        )
        summary = TasksSummaryOut(**summary_data)
        filters = TasksFilterOut(
            area_id=area_id,
            from_=from_dt,
            to=to_dt,
            paid=paid,
            only_finalized=only_finalized,
            external=external,
        )
        return TasksResponse(items=items, summary=summary, filters=filters)

    async def mark_paid(self, data: MarkPaidIn) -> MarkPaidOut:
        paid_at = data.paid_at
        if data.paid and paid_at is None:
            paid_at = datetime.utcnow()
        updated = await self.repo.bulk_mark_paid(data.task_ids, data.paid, paid_at)
        return MarkPaidOut(updated=updated)
