from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.users import ResponseLogin, UserCreate, UserLogin
from app.services.users import UsersService

users_router = APIRouter()


@users_router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    return await service.register(user)


@users_router.post("/login", response_model=ResponseLogin)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    token = await service.login(credentials)
    return {"access_token": token, "token_type": "bearer"}
