# Import các schemas
from .base import PaginationResponse, ResponseSchema
from .tochuc import ToChucCreate, ToChucUpdate, ToChucRead, ToChucDetail
from .nguoidung import (
    NguoiDungCreate, NguoiDungUpdate, NguoiDung as NguoiDungRead, 
    NguoiDungProfileUpdate,
    ChangePasswordRequest,
    UploadAvatarResponse
)
from .token import (
    Token, TokenPayload, TokenData, LoginRequest,
    LoginResponse, PasswordResetRequest, NewPasswordRequest
)
from .lophoc import LopHocCreate, LopHocUpdate, LopHocRead
from .hocsinh import (
    HocSinhCreate, HocSinhUpdate, HocSinhRead,
    GioiTinh, ImportHocSinhRequest
)
from .mauphieu import (
    MauPhieuTraLoiCreate, MauPhieuTraLoiUpdate, MauPhieuTraLoiRead
)
from .baikiemtra import (
    BaiKiemTraCreate, BaiKiemTraUpdate, BaiKiemTraRead,
    BaiKiemTraLopHocCreate, BaiKiemTraLopHocRead, BaiKiemTraWithLopHoc,
    DapAnCreate, DapAnUpdate, DapAnRead, TrangThaiBaiKiemTra
)
from .phieutraloi import (
    PhieuTraLoiCreate, PhieuTraLoiUpdate, PhieuTraLoiRead,
    KetQuaCreate, KetQuaUpdate, KetQuaRead,
    ThongKeKiemTraCreate, ThongKeKiemTraRead,
    ThongKeResponse, KetQuaHocSinhResponse
)
from .caidat import CaiDatCreate, CaiDatUpdate, CaiDatRead
from .taptin import TapTinCreate, TapTinRead
from .user import UserCreate, UserUpdate, UserRead

# Export tất cả schemas
__all__ = [
    # Base
    "PaginationResponse", "ResponseSchema",
    
    # User
    "UserCreate", "UserUpdate", "UserRead",
    
    # ToChuc
    "ToChucCreate", "ToChucUpdate", "ToChucRead", "ToChucDetail",
    
    # NguoiDung
    "NguoiDungCreate", "NguoiDungUpdate", "NguoiDungRead",
    "NguoiDungProfileUpdate",
    "ChangePasswordRequest",
    "UploadAvatarResponse",
    
    # Token
    "Token", "TokenPayload", "TokenData", "LoginRequest",
    "LoginResponse", "PasswordResetRequest", "NewPasswordRequest",
    
    # LopHoc
    "LopHocCreate", "LopHocUpdate", "LopHocRead",
    
    # HocSinh
    "HocSinhCreate", "HocSinhUpdate", "HocSinhRead",
    "GioiTinh", "ImportHocSinhRequest",
    
    # MauPhieu
    "MauPhieuTraLoiCreate", "MauPhieuTraLoiUpdate", "MauPhieuTraLoiRead",
    
    # BaiKiemTra
    "BaiKiemTraCreate", "BaiKiemTraUpdate", "BaiKiemTraRead",
    "BaiKiemTraLopHocCreate", "BaiKiemTraLopHocRead", "BaiKiemTraWithLopHoc",
    "DapAnCreate", "DapAnUpdate", "DapAnRead", "TrangThaiBaiKiemTra",
    
    # PhieuTraLoi
    "PhieuTraLoiCreate", "PhieuTraLoiUpdate", "PhieuTraLoiRead",
    "KetQuaCreate", "KetQuaUpdate", "KetQuaRead",
    "ThongKeKiemTraCreate", "ThongKeKiemTraRead",
    "ThongKeResponse", "KetQuaHocSinhResponse",
    
    # CaiDat
    "CaiDatCreate", "CaiDatUpdate", "CaiDatRead",
    
    # TapTin
    "TapTinCreate", "TapTinRead"
]
