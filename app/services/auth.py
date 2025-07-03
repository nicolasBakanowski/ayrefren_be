from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.db.repositories.users import UsersRepository


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UsersRepository(db)

    async def authenticate_user(self, email: str, password: str):
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def login_token(self, user):
        return create_access_token({"sub": str(user.id), "role": user.role_id})
