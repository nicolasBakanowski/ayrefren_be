from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.constants.response_codes import ResponseCode
from app.schemas.response import ResponseSchema


def success_response(data: Any = None, message: Optional[str] = None) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=ResponseSchema(
            code=ResponseCode.SUCCESS,
            success=True,
            message=message,
            data=jsonable_encoder(data),
        ).model_dump(),
    )
