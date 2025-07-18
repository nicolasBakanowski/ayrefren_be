from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import validate_foreign_keys
from app.db.repositories.work_order_parts import WorkOrderPartsRepository
from app.models.parts import Part
from app.models.work_orders import WorkOrder
from app.schemas.work_order_parts import WorkOrderPartCreate


class WorkOrderPartsService:
    def __init__(self, db: AsyncSession):
        self.repo = WorkOrderPartsRepository(db)

    async def create_part(self, data: WorkOrderPartCreate):
        await validate_foreign_keys(
            self.repo.db,
            {WorkOrder: data.work_order_id, Part: data.part_id},
        )
        return await self.repo.create(data)

    async def list_parts(self, work_order_id: int):
        return await self.repo.list_by_work_order(work_order_id)

    async def delete_part(self, part_id: int):
        deleted = await self.repo.delete(part_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Repuesto no encontrado")
        return {"detail": "Repuesto eliminado"}
