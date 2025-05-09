from typing import Callable

from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.init_db import create_db_and_tables
from scripts.seed_db import seed_db


def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Handler được gọi khi ứng dụng khởi động
    """
    async def start_app() -> None:
        logger.info("Khởi động ứng dụng...")
        
        logger.info(f"Ứng dụng khởi chạy trong môi trường: {settings.ENV}")
        
        # Khởi tạo database khi ứng dụng khởi động
        logger.info("Khởi tạo kết nối database...")
        await create_db_and_tables()
        logger.info("Database đã được khởi tạo thành công!")
        
        # Seed dữ liệu ban đầu vào database
        logger.info("Bắt đầu seed dữ liệu vào database...")
        try:
            await seed_db()
            logger.info("Seed dữ liệu thành công!")
        except Exception as e:
            logger.error(f"Lỗi khi seed dữ liệu: {str(e)}")
            logger.warning("Ứng dụng vẫn tiếp tục chạy mặc dù seed dữ liệu thất bại")
        
        # Khởi tạo thư mục uploads nếu cần
        uploads_dir = settings.ROOT_DIR / settings.UPLOAD_DIR
        if not uploads_dir.exists():
            logger.info(f"Tạo thư mục uploads: {uploads_dir}")
            uploads_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Ứng dụng đã khởi động thành công!")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Handler được gọi khi ứng dụng dừng
    """
    async def stop_app() -> None:
        logger.info("Đang dừng ứng dụng...")
        
        # Đóng kết nối database nếu cần
        # Đóng các kết nối khác nếu cần
        
        logger.info("Ứng dụng đã dừng thành công!")

    return stop_app


def register_app_events(app: FastAPI) -> None:
    """
    Đăng ký các event handler cho FastAPI app
    """
    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app)) 