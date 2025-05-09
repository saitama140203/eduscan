from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from . import Base

class MauPhieuTraLoi(Base):
    __tablename__ = "mauphieutraloi"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maToChuc = Column(Integer, ForeignKey("tochuc.id"), nullable=False)
    maNguoiTao = Column(Integer, ForeignKey("nguoidung.id"), nullable=False)
    tenMauPhieu = Column(String(255), nullable=False)
    soCauHoi = Column(Integer, nullable=False)
    soLuaChonMoiCau = Column(Integer, nullable=False, default=4)
    khoGiay = Column(String(10), nullable=False, default="A4")
    coTuLuan = Column(Boolean, nullable=False, default=False)
    coThongTinHocSinh = Column(Boolean, nullable=False, default=True)
    coLogo = Column(Boolean, nullable=False, default=False)
    cauTrucJSON = Column(JSONB)
    cssFormat = Column(Text)
    laMacDinh = Column(Boolean, nullable=False, default=False)
    laCongKhai = Column(Boolean, nullable=False, default=False)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianCapNhat = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    toChuc = relationship("ToChuc", back_populates="mauPhieuTraLois")
    nguoiTao = relationship("NguoiDung", back_populates="mauPhieuTraLois")
    baiKiemTras = relationship("BaiKiemTra", back_populates="mauPhieu")

    # Indexes
    __table_args__ = (
        Index("idx_mauphieutraloi_tochuc", "maToChuc"),
        Index("idx_mauphieutraloi_nguoitao", "maNguoiTao"),
    ) 