from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import hash_password
from app.models.users import User
from app.schemas.users import UserCreate


class UsersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user_in: UserCreate) -> User:
        hashed_pw = hash_password(user_in.password)
        db_user = User(
            name=user_in.name,
            email=user_in.email,
            password=hashed_pw,
            role_id=user_in.role_id,
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def list(self, role_id: Optional[int] = None) -> list[User]:
        stmt = select(User)
        if role_id is not None:
            stmt = stmt.where(User.role_id == role_id)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, user_id: int, user_in: UserCreate) -> User:
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if user_in.name:
            user.name = user_in.name
        if user_in.email:
            user.email = user_in.email
        if user_in.password:
            user.password = hash_password(user_in.password)
        if user_in.role_id is not None:
            user.role_id = user_in.role_id

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        await self.db.delete(user)
        await self.db.commit()

    async def update_password(self, user_id: int, new_password: str) -> User:
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        user.password = hash_password(new_password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
