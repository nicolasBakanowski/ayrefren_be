from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.core.responses import success_response
from app.schemas.response import ResponseSchema
from app.schemas.work_orders import WorkOrderOut, WorkOrderReviewer
from app.services.work_orders import WorkOrdersService

work_orders_reviewer_router = APIRouter()


@work_orders_reviewer_router.post(
    "/",
    response_model=ResponseSchema[WorkOrderOut],
)
async def assign_reviewer(
    reviewer_in: WorkOrderReviewer,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrdersService(db)
    data = await service.assign_reviewer(
        work_order_id=reviewer_in.work_order_id,
        reviewer_id=reviewer_in.reviewer_id,
    )
    return success_response(data=data)


@work_orders_reviewer_router.delete("/{work_order_id}/{reviewer_id}")
async def remove_reviewer(
    work_order_id: int = Path(..., gt=0),
    reviewer_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrdersService(db)
    data = await service.remove_reviewer(work_order_id, reviewer_id)
    return success_response(data=data)
