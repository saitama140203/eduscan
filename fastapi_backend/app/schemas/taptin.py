from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class TapTinBase(BaseModel):
    """Schema cơ bản cho tập tin."""
    to_chuc_id: Optional[int] = None
    nguoi_dung_id: Optional[int] = None
    ten_tap_tin: Optional[str] = None
    duong_dan: Optional[str] = None
    loai_tap_tin: Optional[str] = None
    kich_thuoc: Optional[int] = None
    thuc_the_nguon: Optional[str] = None
    ma_thuc_the_nguon: Optional[int] = None


class TapTinCreate(TapTinBase):
    """Schema tạo tập tin."""
    to_chuc_id: int
    nguoi_dung_id: int
    ten_tap_tin: str
    duong_dan: str
    loai_tap_tin: str
    kich_thuoc: int


class TapTinUpdate(TapTinBase):
    """Schema cập nhật tập tin."""
    pass


class TapTinRead(TapTinBase):
    """Schema đọc thông tin tập tin."""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TapTinResponse(BaseModel):
    """Schema phản hồi cho tập tin."""
    id: int
    ten_tap_tin: str
    duong_dan: str
    loai_tap_tin: str
    kich_thuoc: int
    created_at: datetime 