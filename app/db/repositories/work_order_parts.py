from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.work_order_parts import WorkOrderPart
from app.schemas.work_order_parts import WorkOrderPartCreate


class WorkOrderPartsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, part_in: WorkOrderPartCreate) -> WorkOrderPart:
        part = WorkOrderPart(**part_in.model_dump())
        self.db.add(part)
        await self.db.commit()
        await self.db.refresh(part)
        return await self.get(part.id)

    async def list_by_work_order(self, work_order_id: int) -> list[WorkOrderPart]:
        result = await self.db.execute(
            select(WorkOrderPart)
            .options(selectinload(WorkOrderPart.work_order))
            .where(WorkOrderPart.work_order_id == work_order_id)
        )
        return result.scalars().all()

    async def delete(self, part_id: int) -> bool:
        part = await self.db.get(WorkOrderPart, part_id)
        if not part:
            return False
        await self.db.delete(part)
        await self.db.commit()
        return True

    async def get(self, work_order_part_id: int) -> WorkOrderPart:
        result = await self.db.execute(
            select(WorkOrderPart)
            .options(selectinload(WorkOrderPart.work_order))
            .where(WorkOrderPart.id == work_order_part_id)
        )

        return result.scalar_one_or_none()

    async def list_names(self) -> list[str]:
        result = await self.db.execute(select(WorkOrderPart.name))
        return [row[0] for row in result.fetchall()]
