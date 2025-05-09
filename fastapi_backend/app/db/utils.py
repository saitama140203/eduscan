from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from .session import get_async_session



async def commit_and_refresh(session: AsyncSession, obj):
    """
    Lưu object vào database và refresh để lấy các giá trị mới từ database
    """
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj 