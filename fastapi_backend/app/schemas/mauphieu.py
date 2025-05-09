from typing import Optional, List
from pydantic import BaseModel


class MauPhieuTraLoiBase(BaseModel):
    """Schema cơ bản cho mẫu phiếu trả lời."""
    ten: Optional[str] = None
    mo_ta: Optional[str] = None
    to_chuc_id: Optional[int] = None
    nguoi_tao_id: Optional[int] = None
    cau_hinh: Optional[dict] = None
    trang_thai: Optional[bool] = True


class MauPhieuTraLoiCreate(MauPhieuTraLoiBase):
    """Schema tạo mẫu phiếu trả lời."""
    ten: str
    to_chuc_id: int
    nguoi_tao_id: int


class MauPhieuTraLoiUpdate(MauPhieuTraLoiBase):
    """Schema cập nhật mẫu phiếu trả lời."""
    pass


class MauPhieuTraLoiRead(MauPhieuTraLoiBase):
    """Schema đọc thông tin mẫu phiếu trả lời."""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True 