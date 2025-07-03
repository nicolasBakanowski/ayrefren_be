from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.db.repositories.users import UsersRepository
from app.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    repo = UsersRepository(db)
    user = await repo.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def admin_only(user: User = Depends(get_current_user)):
    if user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede realizar esta acción")
    return user


def roles_allowed(*allowed_roles):
    def wrapper(user: User = Depends(get_current_user)):
        if user.role.name not in allowed_roles:
            raise HTTPException(status_code=403, detail="No tiene permiso para esta operación")
        return user

    return wrapper
