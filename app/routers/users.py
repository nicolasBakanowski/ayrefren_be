from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN, REVISOR
from app.core.database import get_db
from app.core.dependencies import roles_allowed
from app.models.users import User
from app.schemas.users import ResponseLogin, UserCreate, UserLogin, UserOut
from app.services.users import UsersService

users_router = APIRouter()


@users_router.post("/register", response_model=UserOut)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(roles_allowed(ADMIN, REVISOR)),
):
    service = UsersService(db)
    return await service.register(user)


@users_router.post("/login", response_model=ResponseLogin)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    token = await service.login(credentials)
    return {"access_token": token, "token_type": "bearer"}
