from datetime import datetime

from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.work_order_tasks import WorkOrderTask
from app.models.work_orders import WorkOrder
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

    def _filtered_query(
        self,
        area_id: int,
        paid: bool | None,
        from_dt: datetime | None,
        to_dt: datetime | None,
        only_finalized: bool,
        external: bool | None,
    ):
        query = select(WorkOrderTask)
        if only_finalized:
            query = query.join(WorkOrder).where(WorkOrder.status_id == 3)
        query = query.where(WorkOrderTask.area_id == area_id)
        if external is not None:
            query = query.where(WorkOrderTask.external == external)
        if paid is not None:
            query = query.where(WorkOrderTask.paid == paid)
        if from_dt:
            query = query.where(WorkOrderTask.created_at >= from_dt)
        if to_dt:
            query = query.where(WorkOrderTask.created_at <= to_dt)
        return query

    async def list_tasks_filtered(
        self,
        area_id: int,
        paid: bool | None,
        from_dt: datetime | None,
        to_dt: datetime | None,
        only_finalized: bool,
        external: bool | None,
    ) -> list[WorkOrderTask]:
        query = self._filtered_query(
            area_id, paid, from_dt, to_dt, only_finalized, external
        )
        items_q = query.order_by(WorkOrderTask.created_at)
        items = (await self.db.execute(items_q)).scalars().all()
        return items

    async def aggregate_tasks(
        self,
        area_id: int,
        paid: bool | None,
        from_dt: datetime | None,
        to_dt: datetime | None,
        only_finalized: bool,
        external: bool | None,
    ) -> dict:
        query = self._filtered_query(
            area_id, paid, from_dt, to_dt, only_finalized, external
        )
        agg_q = query.with_only_columns(
            func.coalesce(func.sum(WorkOrderTask.price), 0),
            func.count(),
        ).order_by(None)
        total_amount, count = (await self.db.execute(agg_q)).one()

        by_user_q = query.with_only_columns(
            WorkOrderTask.user_id,
            func.coalesce(func.sum(WorkOrderTask.price), 0),
            func.count(),
        ).group_by(WorkOrderTask.user_id)
        by_user_res = await self.db.execute(by_user_q)
        by_user = [
            {
                "user_id": uid,
                "total_amount": float(amount or 0),
                "count": cnt,
            }
            for uid, amount, cnt in by_user_res.all()
        ]
        return {
            "total_amount": float(total_amount or 0),
            "count": count,
            "by_user": by_user,
        }

    async def bulk_mark_paid(
        self, task_ids: list[int], paid: bool, paid_at: datetime | None
    ) -> int:
        stmt = (
            update(WorkOrderTask)
            .where(WorkOrderTask.id.in_(task_ids))
            .values(paid=paid, paid_at=paid_at)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount or 0
