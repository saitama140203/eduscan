from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import MetaData

# Cấu hình naming convention cho các constraints và keys
convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

# Sử dụng metadata với naming convention
metadata = MetaData(naming_convention=convention)

@as_declarative(metadata=metadata)
class Base:
    """
    Base model class cho tất cả các SQLAlchemy models

    Attributes:
        __tablename__: Tên bảng trong database tự động tạo từ tên class
        id: Primary key column mà mỗi model sẽ kế thừa (sẽ được định nghĩa ở mỗi model cụ thể)
    """
    
    id: Any
    
    # Tạo __tablename__ tự động dựa trên tên class
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Thêm quote=True để giữ nguyên tên cột camelCase
    __table_args__ = {"quote": True} 