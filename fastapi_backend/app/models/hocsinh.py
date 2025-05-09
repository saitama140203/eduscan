from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from . import Base

class HocSinh(Base):
    __tablename__ = "hocsinh"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maLopHoc = Column(Integer, ForeignKey("lophoc.id"), nullable=False)
    maHocSinhTruong = Column(String(50), nullable=False)
    hoTen = Column(String(255), nullable=False)
    ngaySinh = Column(DateTime)
    gioiTinh = Column(String(10))
    soDienThoaiPhuHuynh = Column(String(20))
    emailPhuHuynh = Column(String(255))
    trangThai = Column(Boolean, nullable=False, default=True)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianCapNhat = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lopHoc = relationship("LopHoc", back_populates="hocSinhs")
    phieuTraLois = relationship("PhieuTraLoi", back_populates="hocSinh")
    ketQuas = relationship("KetQua", back_populates="hocSinh")

    # Constraints
    __table_args__ = (
        UniqueConstraint("maHocSinhTruong", "maLopHoc", name="uq_hocsinh_mahocsinhtruong_malophoc"),
        Index("idx_hocsinh_lophoc", "maLopHoc"),
        Index("idx_hocsinh_mahocsinhtruong", "maHocSinhTruong"),
    ) 