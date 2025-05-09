#!/usr/bin/env python3
"""
Script để seed data ban đầu vào database.

Sử dụng:
    poetry run python -m scripts.seed_db
    hoặc
    python scripts/seed_db.py
"""
import asyncio
import logging
from typing import List, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.init_db import create_db_and_tables
from app.db.session import async_session_factory
from app.models.tochuc import ToChuc
from app.models.nguoidung import NguoiDung


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_first_to_chuc(db: AsyncSession) -> ToChuc:
    """
    Tạo tổ chức đầu tiên
    """
    # Kiểm tra xem đã có tổ chức nào chưa
    result = await db.execute(select(ToChuc).limit(1))
    to_chuc = result.scalar_one_or_none()
    
    if to_chuc:
        logger.info(f"Tổ chức đã tồn tại: {to_chuc.tenToChuc}")
        return to_chuc
    
    # Tạo tổ chức mới
    to_chuc = ToChuc(
        tenToChuc="EduScan School",
        loaiToChuc="Trường Học",
        diaChi="Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội",
    )
    db.add(to_chuc)
    await db.commit()
    await db.refresh(to_chuc)
    
    logger.info(f"Đã tạo tổ chức: {to_chuc.tenToChuc}")
    return to_chuc


async def create_first_admin(db: AsyncSession, to_chuc: ToChuc) -> NguoiDung:
    """
    Tạo admin đầu tiên cho tổ chức
    """
    # Kiểm tra xem đã có admin chưa
    result = await db.execute(
        select(NguoiDung).where(NguoiDung.vaiTro == "admin").limit(1)
    )
    admin = result.scalar_one_or_none()
    
    if admin:
        logger.info(f"Admin đã tồn tại: {admin.hoTen}")
        return admin
    
    # Tạo admin mới
    admin_user = NguoiDung(
        email="admin@example.com",
        hoTen="Admin",
        matKhau=get_password_hash("Admin@123"),
        vaiTro="admin",
        trangThai=True,
        toChucId=to_chuc.id,
    )
    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)
    
    logger.info(f"Đã tạo admin: {admin_user.hoTen}")
    return admin_user


async def create_sample_users(db: AsyncSession, to_chuc: ToChuc) -> List[NguoiDung]:
    """
    Tạo một số người dùng mẫu
    """
    # Dữ liệu mẫu người dùng
    users_data = [
        {
            "hoTen": "Giáo Viên A",
            "email": "giaovien.a@example.com",
            "matKhau": get_password_hash("GiaoVien@123"),
            "vaiTro": "teacher",
            "trangThai": True,
            "toChucId": to_chuc.id,
        },
        {
            "hoTen": "Giáo Viên B",
            "email": "giaovien.b@example.com",
            "matKhau": get_password_hash("GiaoVien@123"),
            "vaiTro": "teacher",
            "trangThai": True,
            "toChucId": to_chuc.id,
        },
        {
            "hoTen": "Nhân Viên C",
            "email": "nhanvien.c@example.com",
            "matKhau": get_password_hash("NhanVien@123"),
            "vaiTro": "staff",
            "trangThai": True,
            "toChucId": to_chuc.id,
        },
    ]
    
    created_users = []
    for user_data in users_data:
        # Kiểm tra xem người dùng đã tồn tại chưa
        result = await db.execute(
            select(NguoiDung).where(NguoiDung.email == user_data["email"])
        )
        user = result.scalar_one_or_none()
        
        if user:
            logger.info(f"Người dùng đã tồn tại: {user.hoTen}")
            created_users.append(user)
            continue
        
        # Tạo người dùng mới
        new_user = NguoiDung(**user_data)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"Đã tạo người dùng: {new_user.hoTen}")
        created_users.append(new_user)
    
    return created_users


async def seed_db() -> None:
    """
    Seed dữ liệu ban đầu
    """
    logger.info("Bắt đầu seed database...")
    
    # Tạo tables nếu chưa tồn tại
    await create_db_and_tables()
    
    # Tạo session
    async with async_session_factory() as db:
        # Tạo tổ chức
        to_chuc = await create_first_to_chuc(db)
        
        # Tạo admin
        admin = await create_first_admin(db, to_chuc)
        
        # Tạo người dùng mẫu
        users = await create_sample_users(db, to_chuc)
    
    logger.info("Seed database hoàn tất!")


if __name__ == "__main__":
    try:
        asyncio.run(seed_db())
    except Exception as e:
        logger.error(f"Lỗi khi seed database: {e}")
        raise 