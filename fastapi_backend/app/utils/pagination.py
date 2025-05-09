from typing import Generic, List, Optional, TypeVar, Any, Sequence, Dict, Union
from fastapi import Query, Request
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.schemas.base import PaginatedResponse
from app.db.base import Base

T = TypeVar('T', bound=Base)
ResponseT = TypeVar('ResponseT', bound=BaseModel)


class PaginationParams:
    """
    Tham số phân trang cho API endpoints
    """
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Số trang"),
        limit: int = Query(20, ge=1, le=100, description="Số lượng kết quả mỗi trang"),
        sort_by: Optional[str] = Query(None, description="Sắp xếp theo trường"),
        order: Optional[str] = Query(None, description="Thứ tự sắp xếp (asc/desc)"),
    ):
        self.page = page
        self.limit = limit
        self.sort_by = sort_by
        self.order = order
        
    @property
    def skip(self) -> int:
        """
        Tính offset dựa trên page và limit
        """
        return (self.page - 1) * self.limit


class Paginator(Generic[T, ResponseT]):
    """
    Công cụ phân trang generic để sử dụng với SQLAlchemy
    """
    def __init__(self, model: type[T], schema: type[ResponseT]):
        """
        Khởi tạo paginator với model và schema
        """
        self.model = model
        self.schema = schema
    
    async def paginate(
        self,
        db: AsyncSession,
        query: Optional[Select] = None,
        pagination: Optional[PaginationParams] = None,
        **filters: Any,
    ) -> PaginatedResponse[ResponseT]:
        """
        Phân trang kết quả từ database
        """
        if pagination is None:
            pagination = PaginationParams()
            
        # Tạo query cơ bản nếu không được cung cấp
        if query is None:
            query = select(self.model)
        
        # Áp dụng bộ lọc
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
        
        # Xử lý soft delete nếu model hỗ trợ
        if hasattr(self.model, "daXoa"):
            query = query.where(self.model.daXoa.is_(None))
        
        # Đếm tổng số kết quả (không bao gồm phân trang)
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        
        # Áp dụng sắp xếp
        if pagination.sort_by and hasattr(self.model, pagination.sort_by):
            sort_column = getattr(self.model, pagination.sort_by)
            if pagination.order and pagination.order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        elif hasattr(self.model, "id"):
            # Sắp xếp mặc định theo ID nếu không có sắp xếp nào được chỉ định
            query = query.order_by(self.model.id.asc())
        
        # Áp dụng phân trang
        query = query.offset(pagination.skip).limit(pagination.limit)
        
        # Thực thi query
        result = await db.execute(query)
        items = result.scalars().all()
        
        # Chuyển đổi thành schemas
        schema_items = [self.schema.model_validate(item) for item in items]
        
        # Tạo response phân trang
        return PaginatedResponse.create(
            items=schema_items,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )


def format_page_info(
    request: Request, total_items: int, page: int, limit: int
) -> Dict[str, Any]:
    """
    Tạo thông tin phân trang bao gồm các liên kết prev/next
    """
    total_pages = (total_items + limit - 1) // limit if limit > 0 else 1
    base_url = str(request.url).split("?")[0]
    
    query_params = dict(request.query_params)
    
    # Tạo URL cho trang trước
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None
    
    prev_url = None
    next_url = None
    
    if prev_page:
        query_params["page"] = str(prev_page)
        prev_url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in query_params.items()])}"
    
    if next_page:
        query_params["page"] = str(next_page)
        next_url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in query_params.items()])}"
    
    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "prev": prev_url,
        "next": next_url,
    } 