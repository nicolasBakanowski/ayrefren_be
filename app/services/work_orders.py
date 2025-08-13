from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import validate_foreign_keys
from app.db.repositories.work_orders import WorkOrdersRepository
from app.models.trucks import Truck
from app.models.users import User
from app.models.work_orders import WorkOrderStatus
from app.models.invoices import Invoice
from app.schemas.work_orders import WorkOrderCreate, WorkOrderUpdate


class WorkOrdersService:
    def __init__(self, db: AsyncSession):
        self.repo = WorkOrdersRepository(db)

    async def _is_editable(self, work_order_id: int) -> bool:
        result = await self.repo.db.execute(
            select(Invoice.id).where(Invoice.work_order_id == work_order_id)
        )
        return result.first() is None

    async def _add_editable(self, order):
        order.is_editable = await self._is_editable(order.id)
        return order

    async def create_work_order(self, data: WorkOrderCreate):
        await validate_foreign_keys(
            self.repo.db,
            {
                Truck: data.truck_id,
                WorkOrderStatus: data.status_id,
                User: data.reviewed_by,
            },
        )
        order = await self.repo.create(data)
        return await self._add_editable(order)

    async def get_work_order(self, work_order_id: int):
        work_order = await self.repo.get(work_order_id)
        if not work_order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        return await self._add_editable(work_order)

    async def list_work_orders(self):
        orders = await self.repo.list()
        return [await self._add_editable(o) for o in orders]

    async def update_work_order(self, work_order_id: int, data: WorkOrderUpdate):
        await validate_foreign_keys(self.repo.db, {WorkOrderStatus: data.status_id})
        updated = await self.repo.update(work_order_id, data.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        return await self._add_editable(await self.repo.get(work_order_id))

    async def delete_work_order(self, work_order_id: int):
        deleted = await self.repo.delete(work_order_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        return {"detail": "Orden eliminada"}

    async def assign_reviewer(self, work_order_id: int, reviewer_id: int):
        await self.get_work_order(work_order_id)
        await validate_foreign_keys(self.repo.db, {User: reviewer_id})
        await self.repo.update(work_order_id, {"reviewed_by": reviewer_id})
        return await self._add_editable(await self.repo.get(work_order_id))

    async def remove_reviewer(self, work_order_id: int, reviewer_id: int):
        await self.get_work_order(work_order_id)
        await validate_foreign_keys(self.repo.db, {User: reviewer_id})
        work_order = await self.repo.get(work_order_id)
        if work_order.reviewed_by != reviewer_id:
            raise HTTPException(
                status_code=400, detail="Revisor no asignado a esta orden"
            )
        await self.repo.update(work_order_id, {"reviewed_by": None})
        return await self._add_editable(await self.repo.get(work_order_id))

    async def calculate_total(self, work_order_id: int) -> float:
        order = await self.get_work_order(work_order_id)
        parts_total = 0.0
        for p in order.parts:
            inc = float(p.increment_per_unit or 0)
            parts_total += float(p.unit_price) * p.quantity * (1 + inc / 100)

        tasks_total = sum(float(t.price) for t in order.tasks)
        return parts_total + tasks_total
