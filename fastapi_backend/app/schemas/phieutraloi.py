from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class PhieuTraLoiBase(BaseModel):
    """Schema cơ bản cho phiếu trả lời."""
    hoc_sinh_id: Optional[int] = None
    bai_kiem_tra_id: Optional[int] = None
    thoi_gian_bat_dau: Optional[str] = None
    thoi_gian_ket_thuc: Optional[str] = None
    trang_thai: Optional[bool] = False  # False: đang làm, True: đã nộp


class PhieuTraLoiCreate(PhieuTraLoiBase):
    """Schema tạo phiếu trả lời."""
    hoc_sinh_id: int
    bai_kiem_tra_id: int


class PhieuTraLoiUpdate(PhieuTraLoiBase):
    """Schema cập nhật phiếu trả lời."""
    pass


class PhieuTraLoiRead(PhieuTraLoiBase):
    """Schema đọc thông tin phiếu trả lời."""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True


class KetQuaBase(BaseModel):
    """Schema cơ bản cho kết quả."""
    phieu_tra_loi_id: Optional[int] = None
    dap_an_id: Optional[int] = None
    lua_chon: Optional[str] = None
    diem: Optional[float] = 0


class KetQuaCreate(KetQuaBase):
    """Schema tạo kết quả."""
    phieu_tra_loi_id: int
    dap_an_id: int


class KetQuaUpdate(KetQuaBase):
    """Schema cập nhật kết quả."""
    pass


class KetQuaRead(KetQuaBase):
    """Schema đọc thông tin kết quả."""
    id: int

    class Config:
        orm_mode = True


class ThongKeKiemTraBase(BaseModel):
    """Schema cơ bản cho thống kê kiểm tra."""
    bai_kiem_tra_id: Optional[int] = None
    lop_hoc_id: Optional[int] = None
    tong_so_hoc_sinh: Optional[int] = 0
    so_hoc_sinh_da_nop: Optional[int] = 0
    diem_trung_binh: Optional[float] = 0
    diem_cao_nhat: Optional[float] = 0
    diem_thap_nhat: Optional[float] = 0


class ThongKeKiemTraCreate(ThongKeKiemTraBase):
    """Schema tạo thống kê kiểm tra."""
    bai_kiem_tra_id: int
    lop_hoc_id: int


class ThongKeKiemTraRead(ThongKeKiemTraBase):
    """Schema đọc thông tin thống kê kiểm tra."""
    id: int

    class Config:
        orm_mode = True


class KetQuaHocSinhResponse(BaseModel):
    """Schema phản hồi kết quả học sinh."""
    hoc_sinh_id: int
    ho_ten: str
    ma_hoc_sinh: str
    diem: float
    thoi_gian_lam_bai: Optional[int] = None  # phút
    trang_thai: bool


class ThongKeResponse(BaseModel):
    """Schema phản hồi thống kê."""
    tong_so_hoc_sinh: int
    so_hoc_sinh_da_nop: int
    diem_trung_binh: float
    diem_cao_nhat: float
    diem_thap_nhat: float
    ket_qua: List[KetQuaHocSinhResponse] 