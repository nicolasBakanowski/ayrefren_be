from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.work_orders_mechanic import WorkOrderMechanicRepository
from app.schemas.work_orders_mechanic import WorkOrderMechanicCreate


class WorkOrdersMechanicService:
    def __init__(self, db: AsyncSession):
        self.repo = WorkOrderMechanicRepository(db)

    async def assign_mechanic(self, data: WorkOrderMechanicCreate):
        return await self.repo.assign_mechanic(data)

    async def list_mechanics(self, work_order_id: int):
        return await self.repo.list_mechanics_by_order(work_order_id)

    async def remove_mechanic(self, mechanic_id: int):
        deleted = await self.repo.remove_mechanic(mechanic_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Mecánico no encontrado")
        return {"detail": "Mecánico eliminado"}
