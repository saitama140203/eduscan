from typing import Any, Dict, List, Set, Union
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Thông tin ứng dụng
    PROJECT_NAME: str = "EduScan API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "API Backend cho hệ thống EduScan"
    
    # API config
    API_V1_STR: str = "/api"
    OPENAPI_URL: str = "/openapi.json"
    
    # Project directories
    ROOT_DIR: Path = Path(__file__).parent.parent.parent
    
    # Môi trường
    ENV: str = "development"

    # Security
    SECRET_KEY: str
    ACCESS_SECRET_KEY: str
    RESET_PASSWORD_SECRET_KEY: str
    VERIFICATION_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600
    
    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None
    EXPIRE_ON_COMMIT: bool = False
    MAX_CONNECTIONS: int = 10
    POOL_RECYCLE: int = 3600
    
    # Email
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_SERVER: str | None = None
    MAIL_PORT: int | None = None
    MAIL_FROM_NAME: str = "EduScan"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_DIR: str = "email_templates"
    
    # Tích hợp
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS
    CORS_ORIGINS: Set[str] = {"http://localhost:3000", "http://localhost:8000"}
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Redis (cho background tasks)
    REDIS_URL: str | None = None
    
    # Các cài đặt khác
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore",
        env_nested_delimiter="__",
        case_sensitive=True
    )


# Tạo instance toàn cục của settings
settings = Settings()

# Cấu hình tùy chỉnh dựa trên môi trường
if settings.ENV == "test":
    settings.DATABASE_URL = settings.TEST_DATABASE_URL or settings.DATABASE_URL
    settings.UPLOAD_DIR = Path("test_uploads")

# Export để sử dụng trong toàn bộ ứng dụng
__all__ = ["settings"] 