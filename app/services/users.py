from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.db.repositories.users import UsersRepository
from app.schemas.users import UserCreate, UserLogin


class UsersService:
    def __init__(self, db: AsyncSession):
        self.repo = UsersRepository(db)

    async def register(self, user_in: UserCreate):
        existing = await self.repo.get_by_email(user_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        return await self.repo.create(user_in)

    async def login(self, credentials: UserLogin):
        user = await self.repo.get_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.password):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        return create_access_token({"sub": str(user.id)})
