from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseSchema(BaseModel, Generic[T]):
    code: int
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
