from typing import Any, Optional
from pydantic import BaseModel

class ResponseSchema(BaseModel):
    code: int
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
