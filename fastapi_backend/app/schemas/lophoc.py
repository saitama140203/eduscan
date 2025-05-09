from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .tochuc import ToChucRead
from .nguoidung import NguoiDung


class LopHocBase(BaseModel):
    maToChuc: int
    tenLop: str = Field(..., min_length=1, max_length=100)
    capHoc: Optional[str] = None
    namHoc: Optional[str] = None
    maGiaoVienChuNhiem: Optional[int] = None
    moTa: Optional[str] = None
    trangThai: bool = True


class LopHocCreate(LopHocBase):
    pass


class LopHocUpdate(BaseModel):
    tenLop: Optional[str] = None
    capHoc: Optional[str] = None
    namHoc: Optional[str] = None
    maGiaoVienChuNhiem: Optional[int] = None
    moTa: Optional[str] = None
    trangThai: Optional[bool] = None


class LopHocRead(LopHocBase):
    id: int
    thoiGianTao: datetime
    thoiGianCapNhat: datetime
    toChuc: ToChucRead
    giaoVienChuNhiem: Optional[NguoiDung] = None

    model_config = {"from_attributes": True} 