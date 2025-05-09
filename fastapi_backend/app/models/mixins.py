from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, func, String, Integer, text
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """
    Mixin để bổ sung các trường timestamp tự động cho models
    """
    thoiGianTao = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.utcnow,
        server_default=func.now()
    )
    thoiGianCapNhat = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        server_default=func.now(),
        server_onupdate=func.now()
    )


class PrimaryKeyMixin:
    """
    Mixin để bổ sung primary key tự tăng
    """
    id = Column(Integer, primary_key=True, autoincrement=True)


class UUIDMixin:
    """
    Mixin để bổ sung uuid column
    """
    @declared_attr
    def uuid(cls):
        return Column(
            String(36), 
            unique=True, 
            nullable=False, 
            server_default=text("gen_random_uuid()")
        )


class SoftDeleteMixin:
    """
    Mixin để bổ sung chức năng xóa mềm (soft delete)
    """
    daXoa = Column(
        DateTime(timezone=True), 
        nullable=True,
        default=None
    )
    
    def soft_delete(self) -> None:
        """
        Đánh dấu record là đã xóa thay vì xóa hoàn toàn
        """
        self.daXoa = datetime.utcnow()

    def restore(self) -> None:
        """
        Khôi phục record đã bị xóa mềm
        """
        self.daXoa = None
        
    @property
    def is_deleted(self) -> bool:
        """
        Kiểm tra xem record có bị xóa chưa
        """
        return self.daXoa is not None


class BaseMixin(PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Mixin tổng hợp các tính năng cơ bản
    Bao gồm primary key, timestamps và soft delete
    """
    pass 