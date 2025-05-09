from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from . import Base

class LopHoc(Base):
    __tablename__ = "lophoc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maToChuc = Column(Integer, ForeignKey("tochuc.id"), nullable=False)
    tenLop = Column(String(100), nullable=False)
    capHoc = Column(String(20))
    namHoc = Column(String(20))
    maGiaoVienChuNhiem = Column(Integer, ForeignKey("nguoidung.id"))
    moTa = Column(Text)
    trangThai = Column(Boolean, nullable=False, default=True)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianCapNhat = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    toChuc = relationship("ToChuc", back_populates="lopHocs")
    giaoVienChuNhiem = relationship("NguoiDung", back_populates="lopHocs")
    hocSinhs = relationship("HocSinh", back_populates="lopHoc")
    baiKiemTraLopHocs = relationship("BaiKiemTraLopHoc", back_populates="lopHoc")
    thongKeKiemTras = relationship("ThongKeKiemTra", back_populates="lopHoc")

    # Indexes
    __table_args__ = (
        Index("idx_lophoc_tochuc", "maToChuc"),
        Index("idx_lophoc_giaovien", "maGiaoVienChuNhiem"),
    ) 