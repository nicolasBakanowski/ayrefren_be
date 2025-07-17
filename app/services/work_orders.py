from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.work_orders import WorkOrdersRepository
from app.schemas.work_orders import WorkOrderCreate, WorkOrderUpdate


class WorkOrdersService:
    def __init__(self, db: AsyncSession):
        self.repo = WorkOrdersRepository(db)

    async def create_work_order(self, data: WorkOrderCreate):
        return await self.repo.create(data)

    async def get_work_order(self, work_order_id: int):
        work_order = await self.repo.get(work_order_id)
        if not work_order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        return work_order

    async def list_work_orders(self):
        return await self.repo.list()

    async def update_work_order(self, work_order_id: int, data: WorkOrderUpdate):
        updated = await self.repo.update(work_order_id, data.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        return await self.repo.get(work_order_id)

    async def delete_work_order(self, work_order_id: int):
        deleted = await self.repo.delete(work_order_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        return {"detail": "Orden eliminada"}
