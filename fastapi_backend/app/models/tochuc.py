from sqlalchemy import Column, String, Text, Index, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base
from app.models.mixins import BaseMixin


class LoaiHinhToChuc(enum.Enum):
    CONG_LAP = "Công lập"
    TU_THUC = "Tư thục"
    BAN_CONG = "Bán công"
    DAN_LAP = "Dân lập"
    LIEN_KET = "Liên kết"
    QUOC_TE = "Quốc tế"


class ToChuc(Base, BaseMixin):
    """
    Model lưu trữ thông tin về tổ chức
    """
    # Không cần khai báo __tablename__ vì Base tự tạo
    # Không cần khai báo id, thoiGianTao, thoiGianCapNhat vì được thừa kế từ BaseMixin
    
    tenToChuc = Column(String(255), nullable=False, index=True)
    loaiToChuc = Column(String(50), nullable=False, index=True)
    loaiHinh = Column(Enum(LoaiHinhToChuc), nullable=True)
    diaChi = Column(Text)
    soDienThoai = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    urlLogo = Column(String(255))

    # Indexes
    __table_args__ = (
        Index("ix_tochuc_ten_loai", "tenToChuc", "loaiToChuc"),
    )

    # Relationships
    nguoiDungs = relationship("NguoiDung", back_populates="toChuc", lazy="selectin")
    lopHocs = relationship("LopHoc", back_populates="toChuc", lazy="selectin")
    mauPhieuTraLois = relationship("MauPhieuTraLoi", back_populates="toChuc", lazy="selectin")
    baiKiemTras = relationship("BaiKiemTra", back_populates="toChuc", lazy="selectin")
    caiDats = relationship("CaiDat", back_populates="toChuc", lazy="selectin")
    tapTins = relationship("TapTin", back_populates="toChuc", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<ToChuc(id={self.id}, tenToChuc='{self.tenToChuc}', loaiToChuc='{self.loaiToChuc}')>"