from typing import Optional

from pydantic import BaseModel


class PartBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None


class PartOut(PartBase):
    id: int

    class Config:
        from_attributes = True
