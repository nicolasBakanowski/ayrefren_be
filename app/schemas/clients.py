from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class ClientType(str, Enum):
    persona = "persona"
    empresa = "empresa"


class ClientCreate(BaseModel):
    type: ClientType
    name: str
    document_number: str | None = None
    phone: str | None = None


class ClientOut(ClientCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
