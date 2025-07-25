from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.trucks import Truck
from app.models.work_orders import WorkOrder


class WorkOrdersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, work_order_data) -> WorkOrder:
        work_order = WorkOrder(**work_order_data.dict())
        self.db.add(work_order)
        await self.db.commit()
        await self.db.refresh(work_order)
        return await self.get(work_order.id)

    async def get(self, work_order_id: int) -> WorkOrder | None:
        result = await self.db.execute(
            select(WorkOrder)
            .options(
                selectinload(WorkOrder.status),
                selectinload(WorkOrder.truck).selectinload(Truck.client),
                selectinload(WorkOrder.reviewer),
                selectinload(WorkOrder.mechanics),
                selectinload(WorkOrder.tasks),
                selectinload(WorkOrder.parts),
            )
            .where(WorkOrder.id == work_order_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[WorkOrder]:
        result = await self.db.execute(
            select(WorkOrder).options(
                selectinload(WorkOrder.status),
                selectinload(WorkOrder.truck).selectinload(Truck.client),
                selectinload(WorkOrder.reviewer),
                selectinload(WorkOrder.mechanics),
                selectinload(WorkOrder.tasks),
                selectinload(WorkOrder.parts),
            )
        )
        return result.scalars().all()

    async def update(self, work_order_id: int, data: dict) -> WorkOrder | bool:
        work_order = await self.get(work_order_id)
        if not work_order:
            return False

        for key, value in data.items():
            setattr(work_order, key, value)
        await self.db.commit()
        await self.db.refresh(work_order)
        return await self.get(work_order_id)

    async def delete(self, work_order_id: int) -> bool:
        work_order = await self.get(work_order_id)
        if not work_order:
            return False
        await self.db.delete(work_order)
        await self.db.commit()
        return True
