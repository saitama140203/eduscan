import logging
import sys
from typing import Dict, Any, List
import os
import json
from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging và chuyển sang loguru
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class LoggingConfig(BaseModel):
    """
    Cấu hình logging model dùng để thiết lập hệ thống log
    """
    LOGGER_NAME: str = "eduscan"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LOG_LEVEL: str = "INFO"
    
    # Cấu hình file logging
    LOG_DIR: Path = Path("logs")
    LOG_FILENAME: str = "eduscan.log"
    ROTATION: str = "20 MB"
    RETENTION: str = "1 month"
    COMPRESSION: str = "zip"
    
    # Cấu hình JSON logging
    JSON_LOGS: bool = True
    
    # Danh sách logger cần bắt
    LOGGERS: List[str] = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "sqlalchemy.engine",
        "sqlalchemy.pool",
    ]


def setup_logging():
    """
    Thiết lập logging cho ứng dụng
    """
    config = LoggingConfig()
    
    # Tạo thư mục logs nếu chưa tồn tại
    if not os.path.exists(config.LOG_DIR):
        os.makedirs(config.LOG_DIR)
    
    # Cấu hình loguru
    log_file_path = os.path.join(config.LOG_DIR, config.LOG_FILENAME)
    
    # Định dạng cho file log
    if config.JSON_LOGS:
        log_format = "{{\"timestamp\": \"{time:YYYY-MM-DD HH:mm:ss}\", \"level\": \"{level.name}\", \"message\": \"{message}\", \"name\": \"{name}\", \"function\": \"{function}\", \"line\": \"{line}\"}}"
    else:
        log_format = config.LOG_FORMAT
    
    # Cấu hình loguru
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "format": config.LOG_FORMAT, "level": config.LOG_LEVEL},
            {
                "sink": log_file_path,
                "format": log_format,
                "level": config.LOG_LEVEL,
                "rotation": config.ROTATION,
                "retention": config.RETENTION,
                "compression": config.COMPRESSION,
            },
        ]
    )
    
    # Chặn các standard logger và chuyển sang loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Chặn các logger khác
    for logger_name in config.LOGGERS:
        _logger = logging.getLogger(logger_name)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False
        _logger.level = logging.getLevelName(config.LOG_LEVEL)
    
    return logger 