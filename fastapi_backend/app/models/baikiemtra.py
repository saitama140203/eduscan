from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from . import Base

class BaiKiemTra(Base):
    __tablename__ = "baikiemtra"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maToChuc = Column(Integer, ForeignKey("tochuc.id"), nullable=False)
    maNguoiTao = Column(Integer, ForeignKey("nguoidung.id"), nullable=False)
    maMauPhieu = Column(Integer, ForeignKey("mauphieutraloi.id"), nullable=False)
    tieuDe = Column(String(255), nullable=False)
    monHoc = Column(String(100), nullable=False)
    ngayThi = Column(DateTime)
    thoiGianLamBai = Column(Integer)
    tongSoCau = Column(Integer, nullable=False)
    tongDiem = Column(Numeric(5, 2), nullable=False, default=10.0)
    moTa = Column(Text)
    laDeThiTongHop = Column(Boolean, nullable=False, default=False)
    trangThai = Column(String(20), nullable=False, default="nhap")
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianCapNhat = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    toChuc = relationship("ToChuc", back_populates="baiKiemTras")
    nguoiTao = relationship("NguoiDung", back_populates="baiKiemTras")
    mauPhieu = relationship("MauPhieuTraLoi", back_populates="baiKiemTras")
    baiKiemTraLopHocs = relationship("BaiKiemTraLopHoc", back_populates="baiKiemTra", cascade="all, delete-orphan")
    dapAn = relationship("DapAn", back_populates="baiKiemTra", uselist=False, cascade="all, delete-orphan")
    phieuTraLois = relationship("PhieuTraLoi", back_populates="baiKiemTra")
    ketQuas = relationship("KetQua", back_populates="baiKiemTra")
    thongKeKiemTras = relationship("ThongKeKiemTra", back_populates="baiKiemTra", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_baikiemtra_tochuc", "maToChuc"),
        Index("idx_baikiemtra_nguoitao", "maNguoiTao"),
        Index("idx_baikiemtra_mauphieu", "maMauPhieu"),
    )


class BaiKiemTraLopHoc(Base):
    __tablename__ = "baikiemtra_lophoc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maBaiKiemTra = Column(Integer, ForeignKey("baikiemtra.id", ondelete="CASCADE"), nullable=False)
    maLopHoc = Column(Integer, ForeignKey("lophoc.id", ondelete="CASCADE"), nullable=False)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    baiKiemTra = relationship("BaiKiemTra", back_populates="baiKiemTraLopHocs")
    lopHoc = relationship("LopHoc", back_populates="baiKiemTraLopHocs")

    # Constraints
    __table_args__ = (
        UniqueConstraint("maBaiKiemTra", "maLopHoc", name="uq_baikiemtra_lophoc"),
        Index("idx_baikiemtra_lophoc_bkt", "maBaiKiemTra"),
        Index("idx_baikiemtra_lophoc_lophoc", "maLopHoc"),
    )


class DapAn(Base):
    __tablename__ = "dapan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maBaiKiemTra = Column(Integer, ForeignKey("baikiemtra.id", ondelete="CASCADE"), nullable=False, unique=True)
    dapAnJSON = Column(JSONB, nullable=False)
    diemMoiCauJSON = Column(JSONB)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianCapNhat = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    baiKiemTra = relationship("BaiKiemTra", back_populates="dapAn")

    # Indexes
    __table_args__ = (
        Index("idx_dapan_baikiemtra", "maBaiKiemTra"),
    ) 