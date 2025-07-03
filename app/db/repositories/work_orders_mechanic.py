from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.work_orders_mechanic import WorkOrderMechanic
from app.schemas.work_orders_mechanic import WorkOrderMechanicCreate


class WorkOrderMechanicRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def assign_mechanic(self, mechanic_in: WorkOrderMechanicCreate) -> WorkOrderMechanic:
        mechanic = WorkOrderMechanic(**mechanic_in.dict())
        self.db.add(mechanic)
        await self.db.commit()
        await self.db.refresh(mechanic)
        return mechanic

    async def list_mechanics_by_order(self, work_order_id: int) -> list[WorkOrderMechanic]:
        result = await self.db.execute(
            select(WorkOrderMechanic).where(WorkOrderMechanic.work_order_id == work_order_id))
        return result.scalars().all()

    async def remove_mechanic(self, mechanic_id: int) -> bool:
        mechanic = await self.db.get(WorkOrderMechanic, mechanic_id)
        if not mechanic:
            return False
        await self.db.delete(mechanic)
        await self.db.commit()
        return True
