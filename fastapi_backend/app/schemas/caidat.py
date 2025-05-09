from typing import Optional, Dict, Any
from pydantic import BaseModel


class CaiDatBase(BaseModel):
    """Schema cơ bản cho cài đặt."""
    to_chuc_id: Optional[int] = None
    ten_cai_dat: Optional[str] = None
    mo_ta: Optional[str] = None
    gia_tri: Optional[Dict[str, Any]] = None
    trang_thai: Optional[bool] = True


class CaiDatCreate(CaiDatBase):
    """Schema tạo cài đặt."""
    to_chuc_id: int
    ten_cai_dat: str


class CaiDatUpdate(CaiDatBase):
    """Schema cập nhật cài đặt."""
    pass


class CaiDatRead(CaiDatBase):
    """Schema đọc thông tin cài đặt."""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True 