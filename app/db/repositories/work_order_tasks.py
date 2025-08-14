from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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

    async def get(self, task_id: int) -> WorkOrderTask | None:
        result = await self.db.execute(
            select(WorkOrderTask).where(WorkOrderTask.id == task_id)
        )
        return result.scalar_one_or_none()

    async def update(self, task_id: int, data: dict) -> WorkOrderTask | None:
        task = await self.get(task_id)
        if not task:
            return None
        for key, value in data.items():
            setattr(task, key, value)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task_id: int) -> bool:
        task = await self.db.get(WorkOrderTask, task_id)
        if not task:
            return False
        await self.db.delete(task)
        await self.db.commit()
        return True

    async def bulk_update_paid(
        self, task_ids: list[int], paid: bool
    ) -> list[WorkOrderTask] | None:
        result = await self.db.execute(
            select(WorkOrderTask).where(WorkOrderTask.id.in_(task_ids))
        )
        tasks = result.scalars().all()
        if len(tasks) != len(task_ids):
            return None
        for task in tasks:
            task.paid = paid
        await self.db.commit()
        for task in tasks:
            await self.db.refresh(task)
        return tasks
