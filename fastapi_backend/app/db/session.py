from typing import AsyncGenerator, Generator
from urllib.parse import urlparse

from sqlalchemy import create_engine, Engine, Pool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import logger

# Xử lý URL kết nối database
parsed_db_url = urlparse(settings.DATABASE_URL)

# Tạo async database URL
async_db_url = (
    f"postgresql+asyncpg://{parsed_db_url.username}:{parsed_db_url.password}@"
    f"{parsed_db_url.hostname}{':' + str(parsed_db_url.port) if parsed_db_url.port else ''}"
    f"{parsed_db_url.path}"
)

# Tạo sync database URL
sync_db_url = (
    f"postgresql://{parsed_db_url.username}:{parsed_db_url.password}@"
    f"{parsed_db_url.hostname}{':' + str(parsed_db_url.port) if parsed_db_url.port else ''}"
    f"{parsed_db_url.path}"
)

# Cấu hình engine tùy theo môi trường
if settings.ENV == "production" or settings.ENV == "serverless":
    # Môi trường production hoặc serverless sử dụng NullPool
    # NullPool sẽ đóng kết nối ngay khi không sử dụng, phù hợp cho serverless
    async_engine = create_async_engine(
        async_db_url, 
        poolclass=NullPool, 
        echo=False,
    )
    sync_engine = create_engine(
        sync_db_url, 
        poolclass=NullPool,
        echo=False,
    )
    logger.info("Database engine được cấu hình cho môi trường production/serverless (NullPool)")
else:
    # Môi trường development/test sử dụng connection pool
    async_engine = create_async_engine(
        async_db_url,
        pool_size=settings.MAX_CONNECTIONS, 
        max_overflow=10,
        pool_recycle=settings.POOL_RECYCLE,
        pool_pre_ping=True,
        echo=settings.ENV == "development",
    )
    sync_engine = create_engine(
        sync_db_url, 
        pool_size=settings.MAX_CONNECTIONS,
        max_overflow=10, 
        pool_recycle=settings.POOL_RECYCLE,
        pool_pre_ping=True,
        echo=settings.ENV == "development",
    )
    logger.info("Database engine được cấu hình cho môi trường development/test (ConnectionPool)")

# Tạo sessionmaker
async_session_factory = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=settings.EXPIRE_ON_COMMIT,
    autoflush=False,
    autocommit=False,
)

sync_session_factory = sessionmaker(
    bind=sync_engine,
    expire_on_commit=settings.EXPIRE_ON_COMMIT,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency để lấy database session async cho FastAPI
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

# Alias cho get_db để đảm bảo tương thích
get_async_session = get_db

def get_sync_db() -> Generator[Session, None, None]:
    """
    Dependency để lấy database session sync cho các tác vụ không async
    """
    session = sync_session_factory()
    try:
        yield session 
    finally:
        session.close() 