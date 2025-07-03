# app/schemas/truck.py
from pydantic import BaseModel, conint, constr


class TruckBase(BaseModel):
    client_id: int
    license_plate: constr(min_length=1, max_length=20)
    brand: constr(max_length=50) | None = None
    model: constr(max_length=50) | None = None
    year: conint(gt=1900, lt=2100) | None = None


class TruckCreate(TruckBase):
    pass


class TruckUpdate(BaseModel):
    license_plate: constr(min_length=1, max_length=20) | None = None
    brand: constr(max_length=50) | None = None
    model: constr(max_length=50) | None = None
    year: conint(gt=1900, lt=2100) | None = None


class TruckInDB(TruckBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True
