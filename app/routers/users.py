from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.core.responses import success_response
from app.models.users import User
from app.schemas.users import ChangePasswordSchema, UserCreate, UserOut
from app.schemas.response import ResponseSchema
from app.services.users import UsersService

users_router = APIRouter()


@users_router.get("/", response_model=ResponseSchema[list[UserOut]])
async def list_users(
    role_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = UsersService(db)
    data = await service.list_users(role_id)
    return success_response(data=data)


@users_router.post("/register", response_model=ResponseSchema[UserOut])
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = UsersService(db)
    data = await service.register(user)
    return success_response(data=data)


@users_router.get("/{user_id}", response_model=ResponseSchema[UserOut])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = UsersService(db)
    data = await service.get_user(user_id)
    return success_response(data=data)


@users_router.put("/{user_id}")
async def update_user(
    user_id: int,
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(roles_allowed(ADMIN)),
):
    service = UsersService(db)
    data = await service.update_user(user_id, user)
    return success_response(data=data)


@users_router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(roles_allowed(ADMIN)),
):
    service = UsersService(db)
    data = await service.delete_user(user_id)
    return success_response(data=data)


@users_router.put("/{user_id}/password")
async def change_password(
    user_id: int,
    data: ChangePasswordSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = UsersService(db)
    data = await service.change_password(user_id, data)
    return success_response(data=data)


@users_router.get("/me", response_model=ResponseSchema[UserOut])
async def get_current_user(
    current_user: User = Depends(roles_allowed(ADMIN, REVISOR)),
):
    return success_response(data=current_user)
