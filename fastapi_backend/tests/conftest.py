from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelper
import uuid
import asyncio
import os
from typing import AsyncGenerator, Generator

from app.config import settings
from app.models import User, Base

from app.database import get_user_db, get_async_session
from app.main import app
from app.users import get_jwt_strategy

from app.core.config import settings as core_settings
from app.db.base import Base as db_base
from app.db.init_db import create_db_and_tables, drop_db_and_tables
from app.db.session import get_db
from app.main import app as fastapi_app


# Cấu hình test database
test_db_url = settings.TEST_DATABASE_URL or settings.DATABASE_URL
test_async_engine = create_async_engine(test_db_url)
TestingAsyncSessionLocal = sessionmaker(
    test_async_engine, class_=AsyncSession, expire_on_commit=False
)


# Override dependency get_db trong tests
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Tạo và trả về session mới cho mỗi request trong tests
    """
    async with TestingAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Tạo test app với dependencies đã override
@pytest.fixture
def app() -> FastAPI:
    """
    Trả về FastAPI app với các dependencies đã được override
    """
    fastapi_app.dependency_overrides[get_db] = override_get_db
    return fastapi_app


# Set up và tear down database
@pytest.fixture(scope="session")
async def setup_test_db() -> AsyncGenerator[None, None]:
    """
    Chuẩn bị test database (tạo bảng, setup dữ liệu test, v.v.)
    """
    # Tạo bảng
    async with test_async_engine.begin() as conn:
        await conn.run_sync(db_base.metadata.create_all)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))

    # Thiết lập dữ liệu khởi tạo nếu cần
    # ...
    
    yield
    
    # Xóa database sau khi test hoàn thành
    async with test_async_engine.begin() as conn:
        await conn.run_sync(db_base.metadata.drop_all)


# Test client
@pytest.fixture
async def client(app: FastAPI, setup_test_db) -> AsyncGenerator[AsyncClient, None]:
    """
    Tạo AsyncClient để test API
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# DB session for tests
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Tạo session mới cho mỗi test case
    """
    async with TestingAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


# Event loop
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Tạo event loop mới cho mỗi session test
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def engine():
    """Create a fresh test database engine for each test function."""
    engine = create_async_engine(settings.TEST_DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    """Create a fresh database session for each test."""
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture(scope="function")
async def test_client(db_session):
    """Fixture to create a test client that uses the test database session."""

    # FastAPI-Users database override (wraps session with user operation helpers)
    async def override_get_user_db():
        session = SQLAlchemyUserDatabase(db_session, User)
        try:
            yield session
        finally:
            await db_session.close()

    # General database override (raw session access)
    async def override_get_async_session():
        try:
            yield db_session
        finally:
            await db_session.close()

    # Set up test database overrides
    app.dependency_overrides[get_user_db] = override_get_user_db
    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8000"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def authenticated_user(test_client, db_session):
    """Fixture to create and authenticate a test user directly in the database."""

    # Create user data
    user_data = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "hashed_password": PasswordHelper().hash("TestPassword123#"),
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
    }

    # Create user directly in database
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Generate token using the strategy directly
    strategy = get_jwt_strategy()
    access_token = await strategy.write_token(user)

    # Return both the headers and the user data
    return {
        "headers": {"Authorization": f"Bearer {access_token}"},
        "user": user,
        "user_data": {"email": user_data["email"], "password": "TestPassword123#"},
    }
