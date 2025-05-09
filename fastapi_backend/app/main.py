from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.api.errors.http_errors import (
    http_error_handler,
    validation_exception_handler,
)
from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.events import register_app_events
from app.core.logging import setup_logging
 

# Khởi tạo logging
logger = setup_logging()


# Tạo ứng dụng FastAPI với các cấu hình từ settings
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}{settings.OPENAPI_URL}",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Đăng ký các event handlers (startup, shutdown)
register_app_events(app)


# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Đăng ký các exception handlers
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


# Đăng ký router cho API v1
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


# Root endpoint
@app.get("/", tags=["health"])
async def root():
    """
    Kiểm tra trạng thái hoạt động của API
    """
    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


# Endpoint kiểm tra health
@app.get("/health", tags=["health"])
async def health_check():
    """
    Kiểm tra sức khỏe của hệ thống
    """
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware ghi log cho mỗi request
    """
    # Log thông tin request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Xử lý request
    response = await call_next(request)
    
    # Log thông tin response
    logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code}")
    
    return response


# Thêm thông tin cho OpenAPI
if settings.ENV != "production":
    # Chỉ hiển thị thông tin này trong môi trường không phải production
    from app.api.openapi import custom_openapi
    app.openapi = custom_openapi(app)
