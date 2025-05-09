from typing import Union, Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from app.core.logging import logger
from app.schemas.base import ErrorResponseSchema


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler cho lỗi HTTP từ Starlette
    """
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    
    error_response = ErrorResponseSchema(
        success=False,
        message=exc.detail,
        detail=exc.detail,
        status_code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}",
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handler cho lỗi validation từ request
    """
    error_details = {}
    
    for error in exc.errors():
        loc = ".".join([str(l) for l in error.get("loc", [])])
        if loc:
            error_details[loc] = error.get("msg")
    
    logger.warning(f"Validation error: {error_details}")
    
    error_response = ErrorResponseSchema(
        success=False,
        message="Lỗi xác thực dữ liệu trong request",
        detail="Lỗi xác thực dữ liệu trong request",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        details=error_details,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Handler cho các lỗi chưa được xử lý khác
    """
    logger.exception(f"Unhandled exception: {str(exc)}")
    
    error_message = "Lỗi hệ thống không xác định"
    error_response = ErrorResponseSchema(
        success=False,
        message=error_message,
        detail=str(exc) if str(exc) else error_message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR",
        details={"error": str(exc)} if str(exc) else None,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


def register_exception_handlers(app):
    """
    Đăng ký tất cả exception handlers cho app
    """
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler) 