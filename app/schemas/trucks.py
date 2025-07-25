from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr

from app.schemas.clients import ClientOut


class TruckBase(BaseModel):
    client_id: int
    license_plate: constr(min_length=1, max_length=20)
    brand: constr(max_length=50) | None = None
    model: constr(max_length=50) | None = None


class TruckCreate(TruckBase):
    pass


class TruckUpdate(BaseModel):
    license_plate: constr(min_length=1, max_length=20) | None = None
    brand: constr(max_length=50) | None = None
    model: constr(max_length=50) | None = None


class TruckInDB(TruckBase):
    id: int
    created_at: datetime
    client: Optional[ClientOut] = None

    class Config:
        from_attributes = True
