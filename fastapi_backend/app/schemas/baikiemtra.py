from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from enum import Enum


class TrangThaiBaiKiemTra(str, Enum):
    """Enum trạng thái bài kiểm tra."""
    DRAFT = "draft"
    PUBLISHED = "published"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class DapAnBase(BaseModel):
    """Schema cơ bản cho đáp án."""
    cau_hoi: Optional[str] = None
    lua_chon: Optional[Dict[str, Any]] = None
    dap_an_dung: Optional[str] = None
    diem: Optional[float] = 1.0
    bai_kiem_tra_id: Optional[int] = None


class DapAnCreate(DapAnBase):
    """Schema tạo đáp án."""
    cau_hoi: str
    bai_kiem_tra_id: int


class DapAnUpdate(DapAnBase):
    """Schema cập nhật đáp án."""
    pass


class DapAnRead(DapAnBase):
    """Schema đọc thông tin đáp án."""
    id: int

    class Config:
        orm_mode = True


class BaiKiemTraBase(BaseModel):
    """Schema cơ bản cho bài kiểm tra."""
    ten: Optional[str] = None
    mo_ta: Optional[str] = None
    thoi_gian_lam_bai: Optional[int] = 0  # phút
    thoi_gian_bat_dau: Optional[str] = None
    thoi_gian_ket_thuc: Optional[str] = None
    to_chuc_id: Optional[int] = None
    nguoi_tao_id: Optional[int] = None
    mau_phieu_id: Optional[int] = None
    trang_thai: Optional[TrangThaiBaiKiemTra] = TrangThaiBaiKiemTra.DRAFT


class BaiKiemTraCreate(BaiKiemTraBase):
    """Schema tạo bài kiểm tra."""
    ten: str
    to_chuc_id: int
    nguoi_tao_id: int


class BaiKiemTraUpdate(BaiKiemTraBase):
    """Schema cập nhật bài kiểm tra."""
    pass


class BaiKiemTraRead(BaiKiemTraBase):
    """Schema đọc thông tin bài kiểm tra."""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    dap_an: Optional[List[DapAnRead]] = None

    class Config:
        orm_mode = True


class BaiKiemTraLopHocBase(BaseModel):
    """Schema cơ bản cho liên kết bài kiểm tra - lớp học."""
    bai_kiem_tra_id: Optional[int] = None
    lop_hoc_id: Optional[int] = None


class BaiKiemTraLopHocCreate(BaiKiemTraLopHocBase):
    """Schema tạo liên kết bài kiểm tra - lớp học."""
    bai_kiem_tra_id: int
    lop_hoc_id: int


class BaiKiemTraLopHocRead(BaiKiemTraLopHocBase):
    """Schema đọc thông tin liên kết bài kiểm tra - lớp học."""
    id: int

    class Config:
        orm_mode = True


class BaiKiemTraWithLopHoc(BaiKiemTraRead):
    """Schema bài kiểm tra kèm thông tin lớp học."""
    lop_hoc_ids: Optional[List[int]] = None 