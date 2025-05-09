from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from . import Base
from app.models.mixins import PrimaryKeyMixin, TimestampMixin


class NguoiDung(Base, PrimaryKeyMixin, TimestampMixin):
    """
    Model lưu trữ thông tin người dùng
    """
    # Khai báo rõ ràng tablename
    __tablename__ = "nguoidung"
    
    # Khai báo các cột khớp với tên trong database
    id = Column(Integer, primary_key=True, autoincrement=True)
    toChucId = Column("maToChuc", Integer, ForeignKey("tochuc.id"), nullable=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    matKhau = Column("matKhauMaHoa", String(255), nullable=False)
    hoTen = Column(String(255), nullable=False)
    vaiTro = Column(String(50), nullable=False)
    soDienThoai = Column(String(20), nullable=True)
    urlAnhDaiDien = Column(String(255), nullable=True)
    thoiGianDangNhapCuoi = Column(DateTime, nullable=True)
    trangThai = Column(Boolean, nullable=False)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianCapNhat = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    toChuc = relationship("ToChuc", back_populates="nguoiDungs")
    lopHocs = relationship("LopHoc", back_populates="giaoVienChuNhiem")
    mauPhieuTraLois = relationship("MauPhieuTraLoi", back_populates="nguoiTao")
    baiKiemTras = relationship("BaiKiemTra", back_populates="nguoiTao")
    phieuTraLois = relationship("PhieuTraLoi", back_populates="nguoiQuet")
    tapTins = relationship("TapTin", back_populates="nguoiDung")
    
    # Indexes
    __table_args__ = (
        Index("idx_nguoidung_tochuc", "maToChuc"),
        Index("idx_nguoidung_email", "email"),
        {"quote": True}
    )
    
    def __repr__(self) -> str:
        return f"<NguoiDung(id={self.id}, hoTen='{self.hoTen}', email='{self.email}', vaiTro='{self.vaiTro}')>" 