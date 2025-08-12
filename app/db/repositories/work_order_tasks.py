from datetime import datetime
from typing import List

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.work_order_tasks import WorkOrderTask
from app.schemas.work_order_tasks import WorkOrderTaskCreate


class WorkOrderTasksRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, task_in: WorkOrderTaskCreate) -> WorkOrderTask:
        task = WorkOrderTask(**task_in.dict())
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def list_by_work_order(self, work_order_id: int) -> list[WorkOrderTask]:
        result = await self.db.execute(
            select(WorkOrderTask).where(WorkOrderTask.work_order_id == work_order_id)
        )
        return result.scalars().all()

    async def delete(self, task_id: int) -> bool:
        task = await self.db.get(WorkOrderTask, task_id)
        if not task:
            return False
        await self.db.delete(task)
        await self.db.commit()
        return True

    async def summary(
        self,
        work_area_id: int,
        date_from: datetime,
        date_to: datetime,
        paid: bool,
    ) -> tuple[list[WorkOrderTask], int, float]:
        filters = [
            WorkOrderTask.area_id == work_area_id,
            WorkOrderTask.created_at >= date_from,
            WorkOrderTask.created_at <= date_to,
            WorkOrderTask.paid == paid,
        ]
        result = await self.db.execute(
            select(WorkOrderTask).where(*filters).order_by(WorkOrderTask.created_at)
        )
        tasks = result.scalars().all()
        summary_result = await self.db.execute(
            select(func.count(WorkOrderTask.id), func.coalesce(func.sum(WorkOrderTask.price), 0)).where(
                *filters
            )
        )
        count, total = summary_result.one()
        return tasks, count, float(total)

    async def mark_paid(self, task_ids: List[int], paid_at: datetime) -> int:
        result = await self.db.execute(
            update(WorkOrderTask)
            .where(WorkOrderTask.id.in_(task_ids))
            .values(paid=True, paid_at=paid_at)
        )
        await self.db.commit()
        return result.rowcount
