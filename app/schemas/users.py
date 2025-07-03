from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_id: int
    active: bool

    class Config:
        from_attributes = True


class ResponseLogin(BaseModel):
    access_token: str
    token_type: str = "bearer"