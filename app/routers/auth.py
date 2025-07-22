from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.responses import success_response
from app.schemas.auth import Token
from app.schemas.response import ResponseSchema
from app.services.auth import AuthService

auth_router = APIRouter()


@auth_router.post("/login", response_model=ResponseSchema[Token])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    user = await service.authenticate_user(form_data.username, form_data.password)
    token = service.login_token(user)
    return success_response(
        data={
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "email": user.email,
                "role_id": user.role_id,
            },
        }
    )


@auth_router.post("/token", response_model=Token, include_in_schema=False)
async def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.authenticate_user(form_data.username, form_data.password)
    access_token = service.login_token(user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"email": user.email, "role_id": user.role_id},
    }
