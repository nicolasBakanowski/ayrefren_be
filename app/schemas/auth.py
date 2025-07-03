# app/auth/schemas.py
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str | None = None
    role: int | None = None
    exp: int | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role_id: int
    active: bool

    class Config:
        from_attributes = True
