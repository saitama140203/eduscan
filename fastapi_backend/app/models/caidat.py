from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from . import Base

class CaiDat(Base):
    __tablename__ = "caidat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maToChuc = Column(Integer, ForeignKey("tochuc.id"), nullable=False)
    tuKhoa = Column(String(100), nullable=False)
    giaTri = Column(Text)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianCapNhat = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    toChuc = relationship("ToChuc", back_populates="caiDats")

    # Constraints
    __table_args__ = (
        UniqueConstraint("maToChuc", "tuKhoa", name="uq_caidat_tochuc_tukhoa"),
        Index("idx_caidat_tochuc", "maToChuc"),
    )


class TapTin(Base):
    __tablename__ = "taptin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maNguoiDung = Column(Integer, ForeignKey("nguoidung.id"), nullable=False)
    maToChuc = Column(Integer, ForeignKey("tochuc.id"), nullable=False)
    tenTapTin = Column(String(255), nullable=False)
    duongDan = Column(String(500), nullable=False)
    loaiTapTin = Column(String(100), nullable=False)
    kichThuoc = Column(Integer, nullable=False)
    thucTheNguon = Column(String(50))
    maThucTheNguon = Column(Integer)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    nguoiDung = relationship("NguoiDung", back_populates="tapTins")
    toChuc = relationship("ToChuc", back_populates="tapTins")

    # Indexes
    __table_args__ = (
        Index("idx_taptin_nguoidung", "maNguoiDung"),
        Index("idx_taptin_tochuc", "maToChuc"),
        Index("idx_taptin_thucthe", "thucTheNguon", "maThucTheNguon"),
    ) 