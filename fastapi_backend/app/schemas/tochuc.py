from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class LoaiToChuc(str, Enum):
    TRUONG_HOC = "TRUONG_HOC"
    TO_CHUC = "TO_CHUC"
    CA_NHAN = "CA_NHAN"


class LoaiHinhToChuc(str, Enum):
    CONG_LAP = "CONG_LAP"
    TU_THUC = "TU_THUC"
    BAN_CONG = "BAN_CONG"
    DAN_LAP = "DAN_LAP"
    LIEN_KET = "LIEN_KET"
    QUOC_TE = "QUOC_TE"


class ToChucBase(BaseModel):
    tenToChuc: str = Field(..., min_length=2, max_length=255)
    loaiToChuc: LoaiToChuc
    loaiHinh: Optional[LoaiHinhToChuc] = None
    diaChi: Optional[str] = None
    soDienThoai: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    urlLogo: Optional[str] = None


class ToChucCreate(ToChucBase):
    pass


class ToChucUpdate(BaseModel):
    tenToChuc: Optional[str] = None
    loaiToChuc: Optional[LoaiToChuc] = None
    loaiHinh: Optional[LoaiHinhToChuc] = None
    diaChi: Optional[str] = None
    soDienThoai: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    urlLogo: Optional[str] = None


class ToChucRead(ToChucBase):
    id: int
    thoiGianTao: datetime
    thoiGianCapNhat: datetime

    model_config = {"from_attributes": True}


class ToChucDetail(ToChucRead):
    soNguoiDung: Optional[int] = 0
    soLopHoc: Optional[int] = 0