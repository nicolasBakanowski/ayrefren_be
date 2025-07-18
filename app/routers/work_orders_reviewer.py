from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, MECHANIC, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.schemas.work_orders import (
    WorkOrderReviewer,
)
from app.services.work_orders import WorkOrdersService
from app.services.users import UsersService

work_orders_reviewer_router = APIRouter()


@work_orders_reviewer_router.post("/",)
async def assign_reviewer(
    reviewer_in: WorkOrderReviewer,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrdersService(db)
    user_service = UsersService(db)
    reviewer = await user_service.get_user(reviewer_in.reviewer_id)
    return await service.assign_reviewer(
        work_order_id=reviewer_in.work_order_id,
        reviewer_id=reviewer_in.reviewer_id,
    )


@work_orders_reviewer_router.delete("/{work_order_id}/{reviewer_id}")
async def remove_reviewer(
    work_order_id: int = Path(..., gt=0),
    reviewer_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(roles_allowed(ADMIN)),
):
    service = WorkOrdersService(db)
    user_service = UsersService(db)
    reviewer = await user_service.get_user(reviewer_id)
    return await service.remove_reviewer(work_order_id, reviewer_id)

