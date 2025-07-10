from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.db.repositories.users import UsersRepository
from app.schemas.users import ChangePasswordSchema, UserCreate, UserLogin


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

    async def get_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    async def list_users(self, role_id: int = None):
        return await self.repo.list(role_id)

    async def update_user(self, user_id: int, user_in: UserCreate):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return await self.repo.update(user_id, user_in)

    async def delete_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        await self.repo.delete(user_id)
        return {"detail": "Usuario eliminado exitosamente"}

    async def change_password(
            self, user_id: int, change_password_data: ChangePasswordSchema
    ):
        old_password = change_password_data.old_password
        new_password = change_password_data.new_password
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if not verify_password(old_password, user.password):
            raise HTTPException(status_code=401, detail="Contraseña antigua incorrecta")
        return await self.repo.update_password(user_id, new_password)
