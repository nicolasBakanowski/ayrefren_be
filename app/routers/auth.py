from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import Token
from app.services.auth import AuthService

auth_router = APIRouter()


@auth_router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    user = await service.authenticate_user(form_data.username, form_data.password)
    token = service.login_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "role_id": user.role_id,
        },
    }
