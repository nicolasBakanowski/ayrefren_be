from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.models.users import User
from app.schemas.users import UserCreate, UserOut
from app.services.users import UsersService

users_router = APIRouter()


@users_router.get("/", response_model=List[UserOut])
async def list_users(
        role_id: int = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = UsersService(db)
    return await service.list_users(role_id)


@users_router.post("/register", response_model=UserOut)
async def register(
        user: UserCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = UsersService(db)
    return await service.register(user)


@users_router.get("/me", response_model=UserOut)
async def get_current_user(
        current_user: User = Depends(roles_allowed(ADMIN, REVISOR)),
):
    return current_user
