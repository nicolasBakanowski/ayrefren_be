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

    async def delete(self, task_id: int) -> bool:
        task = await self.db.get(WorkOrderTask, task_id)
        if not task:
            return False
        await self.db.delete(task)
        await self.db.commit()
        return True
