from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from . import Base

class PhieuTraLoi(Base):
    __tablename__ = "phieutraloi"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maBaiKiemTra = Column(Integer, ForeignKey("baikiemtra.id"), nullable=False)
    maHocSinh = Column(Integer, ForeignKey("hocsinh.id"), nullable=False)
    maNguoiQuet = Column(Integer, ForeignKey("nguoidung.id"), nullable=False)
    urlHinhAnh = Column(String(255))
    urlHinhAnhXuLy = Column(String(255))
    cauTraLoiJSON = Column(JSONB)
    daXuLyHoanTat = Column(Boolean, nullable=False, default=False)
    doTinCay = Column(Numeric(5, 2))
    canhBaoJSON = Column(JSONB)
    thoiGianQuet = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianCapNhat = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    baiKiemTra = relationship("BaiKiemTra", back_populates="phieuTraLois")
    hocSinh = relationship("HocSinh", back_populates="phieuTraLois")
    nguoiQuet = relationship("NguoiDung", back_populates="phieuTraLois")
    ketQua = relationship("KetQua", back_populates="phieuTraLoi", uselist=False, cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_phieutraloi_baikiemtra", "maBaiKiemTra"),
        Index("idx_phieutraloi_hocsinh", "maHocSinh"),
        Index("idx_phieutraloi_nguoiquet", "maNguoiQuet"),
    )


class KetQua(Base):
    __tablename__ = "ketqua"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maPhieuTraLoi = Column(Integer, ForeignKey("phieutraloi.id", ondelete="CASCADE"), nullable=False, unique=True)
    maBaiKiemTra = Column(Integer, ForeignKey("baikiemtra.id"), nullable=False)
    maHocSinh = Column(Integer, ForeignKey("hocsinh.id"), nullable=False)
    diem = Column(Numeric(5, 2), nullable=False)
    soCauDung = Column(Integer, nullable=False)
    soCauSai = Column(Integer, nullable=False)
    soCauChuaTraLoi = Column(Integer, nullable=False)
    chiTietJSON = Column(JSONB)
    diemTheoMonJSON = Column(JSONB)
    thuHangTrongLop = Column(Integer)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianCapNhat = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    phieuTraLoi = relationship("PhieuTraLoi", back_populates="ketQua")
    baiKiemTra = relationship("BaiKiemTra", back_populates="ketQuas")
    hocSinh = relationship("HocSinh", back_populates="ketQuas")

    # Indexes
    __table_args__ = (
        Index("idx_ketqua_phieutraloi", "maPhieuTraLoi"),
        Index("idx_ketqua_baikiemtra", "maBaiKiemTra"),
        Index("idx_ketqua_hocsinh", "maHocSinh"),
    )


class ThongKeKiemTra(Base):
    __tablename__ = "thongkekiemtra"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maBaiKiemTra = Column(Integer, ForeignKey("baikiemtra.id", ondelete="CASCADE"), nullable=False)
    maLopHoc = Column(Integer, ForeignKey("lophoc.id"), nullable=False)
    soLuongThamGia = Column(Integer, nullable=False, default=0)
    diemTrungBinh = Column(Numeric(5, 2))
    diemCaoNhat = Column(Numeric(5, 2))
    diemThapNhat = Column(Numeric(5, 2))
    diemTrungVi = Column(Numeric(5, 2))
    doLechChuan = Column(Numeric(5, 2))
    thongKeCauHoiJSON = Column(JSONB)
    phanLoaiDoKhoJSON = Column(JSONB)
    phanBoDiemJSON = Column(JSONB)
    thoiGianTao = Column(DateTime, nullable=False, default=datetime.utcnow)
    thoiGianCapNhat = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    baiKiemTra = relationship("BaiKiemTra", back_populates="thongKeKiemTras")
    lopHoc = relationship("LopHoc", back_populates="thongKeKiemTras")

    # Constraints
    __table_args__ = (
        UniqueConstraint("maBaiKiemTra", "maLopHoc", name="uq_thongkekiemtra_baikiemtra_lophoc"),
        Index("idx_thongkekiemtra_baikiemtra", "maBaiKiemTra"),
        Index("idx_thongkekiemtra_lophoc", "maLopHoc"),
    ) 