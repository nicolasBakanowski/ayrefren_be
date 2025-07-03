from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.schemas.work_orders_mechanic import WorkOrderMechanicCreate, WorkOrderMechanicOut
from app.services.work_orders_mechanic import WorkOrdersMechanicService

work_orders_mechanic_router = APIRouter()


@work_orders_mechanic_router.post("/", response_model=WorkOrderMechanicOut,
                                  dependencies=[Depends(roles_allowed("admin", "revisor"))])
async def assign_mechanic(mechanic_in: WorkOrderMechanicCreate, db: AsyncSession = Depends(get_db)):
    service = WorkOrdersMechanicService(db)
    return await service.assign_mechanic(mechanic_in)


@work_orders_mechanic_router.get("/{work_order_id}", response_model=list[WorkOrderMechanicOut],
                                 dependencies=[Depends(roles_allowed("admin", "revisor", "mecanico"))])
async def list_mechanics(work_order_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    service = WorkOrdersMechanicService(db)
    return await service.list_mechanics(work_order_id)


@work_orders_mechanic_router.delete("/{mechanic_id}", dependencies=[Depends(roles_allowed("admin"))])
async def remove_mechanic(mechanic_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    service = WorkOrdersMechanicService(db)
    return await service.remove_mechanic(mechanic_id)
