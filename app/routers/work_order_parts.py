from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.schemas.work_order_parts import WorkOrderPartCreate, WorkOrderPartOut
from app.services.work_order_parts import WorkOrderPartsService

work_order_parts_router = APIRouter()


@work_order_parts_router.post("/", response_model=WorkOrderPartOut,
                              dependencies=[Depends(roles_allowed("admin", "revisor", "mecanico"))])
async def add_part(part_in: WorkOrderPartCreate, db: AsyncSession = Depends(get_db)):
    service = WorkOrderPartsService(db)
    return await service.create_part(part_in)


@work_order_parts_router.get("/{work_order_id}", response_model=list[WorkOrderPartOut],
                             dependencies=[Depends(roles_allowed("admin", "revisor", "mecanico"))])
async def list_parts(work_order_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    service = WorkOrderPartsService(db)
    return await service.list_parts(work_order_id)


@work_order_parts_router.delete("/{part_id}", dependencies=[Depends(roles_allowed("admin"))])
async def remove_part(part_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    service = WorkOrderPartsService(db)
    return await service.delete_part(part_id)
