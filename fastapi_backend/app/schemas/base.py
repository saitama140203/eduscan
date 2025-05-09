from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

T = TypeVar('T')

class BaseSchema(BaseModel):
    """Schema cơ bản cho tất cả các đối tượng."""
    model_config = ConfigDict(
        extra="ignore",
    )

class IDSchema(BaseModel):
    """Schema cho đối tượng có ID."""
    id: int = Field(..., gt=0)

class TimestampSchema(BaseModel):
    """Schema cho đối tượng có thông tin thời gian tạo và cập nhật."""
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class PaginationResponse(BaseModel, Generic[T]):
    """Schema phản hồi phân trang chuẩn."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class ErrorResponseSchema(BaseModel):
    """Schema phản hồi lỗi chuẩn."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None
    status_code: Optional[int] = None
    detail: Optional[str] = None

class ResponseSchema(BaseModel, Generic[T]):
    """Schema phản hồi chuẩn."""
    success: bool = True
    message: str = "Thành công"
    data: Optional[T] = None 