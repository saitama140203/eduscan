from datetime import datetime
from enum import Enum
from typing import Optional, Annotated

from pydantic import BaseModel, Field, EmailStr

from .lophoc import LopHocRead


class GioiTinh(str, Enum):
    NAM = "Nam"
    NU = "Nữ"
    KHAC = "Khác"


# ===== Base model cho học sinh =====
class HocSinhBase(BaseModel):
    maLopHoc: int
    maHocSinhTruong: Annotated[str, Field(min_length=1, max_length=50)]
    hoTen: Annotated[str, Field(min_length=2, max_length=255)]
    ngaySinh: Optional[datetime] = None
    gioiTinh: Optional[GioiTinh] = None
    soDienThoaiPhuHuynh: Optional[str] = None
    emailPhuHuynh: Optional[EmailStr] = None
    trangThai: bool = True


# ===== Tạo mới học sinh =====
class HocSinhCreate(HocSinhBase):
    pass


# ===== Cập nhật học sinh =====
class HocSinhUpdate(BaseModel):
    maLopHoc: Optional[int] = None
    maHocSinhTruong: Optional[str] = None
    hoTen: Optional[str] = None
    ngaySinh: Optional[datetime] = None
    gioiTinh: Optional[GioiTinh] = None
    soDienThoaiPhuHuynh: Optional[str] = None
    emailPhuHuynh: Optional[EmailStr] = None
    trangThai: Optional[bool] = None


# ===== Thông tin đọc học sinh đầy đủ (bao gồm thông tin lớp) =====
class HocSinhRead(HocSinhBase):
    id: int
    thoiGianTao: datetime
    thoiGianCapNhat: datetime
    lopHoc: LopHocRead

    model_config = {"from_attributes": True}


# ===== Yêu cầu import học sinh từ file =====
class ImportHocSinhRequest(BaseModel):
    maLopHoc: int
    fileUrl: str
