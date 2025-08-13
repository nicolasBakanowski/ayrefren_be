from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import validate_foreign_keys
from app.db.repositories.work_order_parts import WorkOrderPartsRepository
from app.models.work_orders import WorkOrder
from app.models.invoices import Invoice
from app.schemas.work_order_parts import WorkOrderPartCreate, WorkOrderPartUpdate


class WorkOrderPartsService:
    def __init__(self, db: AsyncSession):
        self.repo = WorkOrderPartsRepository(db)

    async def _ensure_editable(self, work_order_id: int):
        result = await self.repo.db.execute(
            select(Invoice.id).where(Invoice.work_order_id == work_order_id)
        )
        if result.first():
            raise HTTPException(
                status_code=400, detail="La orden ya está facturada"
            )

    async def create_part(self, data: WorkOrderPartCreate):
        await validate_foreign_keys(
            self.repo.db,
            {WorkOrder: data.work_order_id},
        )
        await self._ensure_editable(data.work_order_id)
        return await self.repo.create(data)

    async def list_parts(self, work_order_id: int):
        return await self.repo.list_by_work_order(work_order_id)

    async def update_part(self, part_id: int, data: WorkOrderPartUpdate):
        part = await self.repo.get(part_id)
        if not part:
            raise HTTPException(status_code=404, detail="Repuesto no encontrado")
        await self._ensure_editable(part.work_order_id)
        if data.work_order_id and data.work_order_id != part.work_order_id:
            await validate_foreign_keys(self.repo.db, {WorkOrder: data.work_order_id})
            await self._ensure_editable(data.work_order_id)
        updated = await self.repo.update(part_id, data.dict(exclude_unset=True))
        return updated

    async def delete_part(self, part_id: int):
        part = await self.repo.get(part_id)
        if not part:
            raise HTTPException(status_code=404, detail="Repuesto no encontrado")
        await self._ensure_editable(part.work_order_id)
        deleted = await self.repo.delete(part_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Repuesto no encontrado")
        return {"detail": "Repuesto eliminado"}

    async def list_names(self):
        return await self.repo.list_names()
