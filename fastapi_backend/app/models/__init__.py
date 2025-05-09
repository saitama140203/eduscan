from app.db.base import Base
from .mixins import BaseMixin
from .nguoidung import NguoiDung

from .tochuc import ToChuc
from .lophoc import LopHoc
from .hocsinh import HocSinh
from .mauphieu import MauPhieuTraLoi
from .baikiemtra import BaiKiemTra, BaiKiemTraLopHoc, DapAn
from .phieutraloi import PhieuTraLoi, KetQua, ThongKeKiemTra
from .caidat import CaiDat, TapTin


# Export tất cả models
__all__ = [
    "Base",
    "User",
    "ToChuc",
    "NguoiDung",
    "LopHoc",
    "HocSinh",
    "MauPhieuTraLoi",
    "BaiKiemTra",
    "BaiKiemTraLopHoc",
    "DapAn",
    "PhieuTraLoi",
    "KetQua",
    "ThongKeKiemTra",
    "CaiDat",
    "TapTin"
]
