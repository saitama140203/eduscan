from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from app.schemas.base import BaseSchema


class Token(BaseSchema):
    """
    Schema cho token trả về sau khi xác thực
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseSchema):
    """
    Schema cho payload của JWT token
    """
    sub: Optional[str] = None
    exp: Optional[int] = None
    scopes: List[str] = []


class TokenData(BaseSchema):
    """
    Schema cho dữ liệu được giải mã từ token
    """
    user_id: Optional[str] = None
    scopes: List[str] = []


class LoginRequest(BaseSchema):
    """
    Schema cho yêu cầu đăng nhập
    """
    email: str
    password: str
    
    @validator("email")
    def username_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Email không được để trống")
        return v
    
    @validator("password")
    def password_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Mật khẩu không được để trống")
        return v


class LoginResponse(BaseSchema):
    """
    Schema cho phản hồi đăng nhập thành công
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    email: EmailStr
    hoTen: str
    vaiTro: str


class PasswordResetRequest(BaseSchema):
    """
    Schema cho yêu cầu khôi phục mật khẩu
    """
    email: EmailStr


class NewPasswordRequest(BaseSchema):
    """
    Schema cho yêu cầu đặt mật khẩu mới
    """
    token: str
    password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Mật khẩu xác nhận không khớp')
        return v 