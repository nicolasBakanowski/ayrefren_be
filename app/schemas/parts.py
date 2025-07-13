from pydantic import BaseModel
from typing import Optional


class PartBase(BaseModel):
    name: str
    price: float
    cost: float
    description: Optional[str] = None


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    description: Optional[str] = None


class PartOut(PartBase):
    id: int

    class Config:
        from_attributes = True
