from sqlalchemy import text

from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base
from app.db.session import async_engine

# Import tất cả các models để SQLAlchemy biết
from app.models import (
    tochuc,
    nguoidung,
    lophoc,
    hocsinh,
    mauphieu,
    baikiemtra,
    phieutraloi,
    caidat,
)


async def create_db_and_tables() -> None:
    """
    Tạo tất cả các bảng trong database nếu chưa tồn tại
    """
    try:
        # Tạo tất cả các bảng
        async with async_engine.begin() as conn:
            # Kiểm tra kết nối database
            await conn.execute(text("SELECT 1"))
            logger.info("Kết nối tới database thành công")
            
            # Tạo các bảng nếu chưa tồn tại
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Đã tạo tất cả các bảng trong database")
            
            # Kiểm tra và tạo extension uuid-ossp nếu chưa có
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
            
        logger.info("Khởi tạo database thành công")
    except Exception as e:
        logger.error(f"Lỗi khởi tạo database: {str(e)}")
        raise


async def drop_db_and_tables() -> None:
    """
    Xóa tất cả các bảng trong database - CHỈ DÙNG TRONG TESTS
    """
    if settings.ENV not in ["test", "development"]:
        logger.warning("Không thể xóa database trong môi trường không phải test/development")
        return
        
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("Đã xóa tất cả các bảng trong database")
    except Exception as e:
        logger.error(f"Lỗi xóa database: {str(e)}")
        raise 