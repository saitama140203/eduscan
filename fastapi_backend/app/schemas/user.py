from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Schema cơ bản cho người dùng."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """Schema tạo người dùng."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(UserBase):
    """Schema cập nhật người dùng."""
    password: Optional[str] = Field(None, min_length=8)


class UserRead(UserBase):
    """Schema đọc thông tin người dùng."""
    id: int

    class Config:
        orm_mode = True 