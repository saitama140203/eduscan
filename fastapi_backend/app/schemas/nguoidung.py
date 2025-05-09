from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict

from app.schemas.base import BaseSchema, IDSchema, TimestampSchema


class NguoiDungBase(BaseSchema):
    """
    Schema cơ bản cho NguoiDung
    """
    hoTen: str
    email: EmailStr
    vaiTro: str = Field(default="user")
    toChucId: int


class NguoiDungCreate(NguoiDungBase):
    """
    Schema để tạo NguoiDung mới
    """
    matKhau: str = Field(..., min_length=8)
    xacNhanMatKhau: str = Field(..., min_length=8)
    
    @validator('xacNhanMatKhau')
    def passwords_match(cls, v, values, **kwargs):
        if 'matKhau' in values and v != values['matKhau']:
            raise ValueError('Mật khẩu xác nhận không khớp')
        return v


class NguoiDungUpdate(BaseSchema):
    """
    Schema để cập nhật NguoiDung
    """
    hoTen: Optional[str] = None
    email: Optional[EmailStr] = None
    matKhau: Optional[str] = None
    vaiTro: Optional[str] = None
    trangThai: Optional[str] = None
    toChucId: Optional[int] = None
    
    model_config = ConfigDict(
        extra="ignore",
    )


class NguoiDungInDB(NguoiDungBase, IDSchema, TimestampSchema):
    """
    Schema cho NguoiDung trong database
    """
    trangThai: str
    
    model_config = ConfigDict(
        from_attributes=True,
    )


class NguoiDung(NguoiDungInDB):
    """
    Schema đầy đủ cho NguoiDung trả về qua API
    """
    pass


class NguoiDungWithoutToChuc(NguoiDungInDB):
    """
    Schema cho NguoiDung không bao gồm thông tin ToChuc
    """
    pass


class NguoiDungProfileUpdate(BaseSchema):
    """
    Schema cho cập nhật profile của người dùng
    """
    hoTen: Optional[str] = None
    email: Optional[EmailStr] = None
    
    model_config = ConfigDict(
        extra="ignore",
    )


class ChangePasswordRequest(BaseSchema):
    """
    Schema cho đổi mật khẩu
    """
    matKhauHienTai: str
    matKhauMoi: str = Field(..., min_length=8)
    xacNhanMatKhauMoi: str
    
    @validator('xacNhanMatKhauMoi')
    def passwords_match(cls, v, values, **kwargs):
        if 'matKhauMoi' in values and v != values['matKhauMoi']:
            raise ValueError('Mật khẩu xác nhận không khớp')
        return v


class VaiTroNguoiDung(str, Enum):
    """
    Enum cho vai trò người dùng
    """
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class UploadAvatarResponse(BaseModel):
    """Schema cho phản hồi upload avatar."""
    url_anh_dai_dien: str 