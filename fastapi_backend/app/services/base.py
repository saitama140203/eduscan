from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

# Định nghĩa generic type
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class cho tất cả các service với các thao tác CRUD cơ bản
    """
    
    def __init__(self, db_session: AsyncSession, model: Type[ModelType]) -> None:
        """
        Khởi tạo service với session và model
        """
        self.db = db_session
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Lấy đối tượng theo ID
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, **filters
    ) -> List[ModelType]:
        """
        Lấy nhiều đối tượng với phân trang và lọc
        """
        query = select(self.model)
        
        # Áp dụng các bộ lọc nếu có
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)
                
        # Kiểm tra xem model có hỗ trợ soft delete không
        if hasattr(self.model, "daXoa"):
            query = query.where(self.model.daXoa.is_(None))
            
        # Thêm phân trang
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count(self, **filters) -> int:
        """
        Đếm số lượng đối tượng theo bộ lọc
        """
        query = select(func.count()).select_from(self.model)
        
        # Áp dụng các bộ lọc nếu có
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)
                
        # Kiểm tra xem model có hỗ trợ soft delete không
        if hasattr(self.model, "daXoa"):
            query = query.where(self.model.daXoa.is_(None))
            
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Tạo đối tượng mới
        """
        obj_data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Cập nhật đối tượng
        """
        obj_data = db_obj.__dict__
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update_by_id(
        self, *, id: int, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Cập nhật đối tượng theo ID
        """
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        return await self.update(db_obj=db_obj, obj_in=obj_in)
    
    async def delete(self, *, db_obj: ModelType) -> ModelType:
        """
        Xóa đối tượng (soft delete nếu hỗ trợ, hard delete nếu không)
        """
        if hasattr(db_obj, "soft_delete") and callable(getattr(db_obj, "soft_delete")):
            # Soft delete nếu model hỗ trợ
            db_obj.soft_delete()
            self.db.add(db_obj)
            await self.db.commit()
            return db_obj
        else:
            # Hard delete nếu không hỗ trợ soft delete
            await self.db.delete(db_obj)
            await self.db.commit()
            return db_obj
    
    async def delete_by_id(self, id: int) -> Optional[ModelType]:
        """
        Xóa đối tượng theo ID
        """
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        return await self.delete(db_obj=db_obj)
    
    async def restore(self, *, db_obj: ModelType) -> Optional[ModelType]:
        """
        Khôi phục đối tượng đã bị xóa mềm
        """
        if hasattr(db_obj, "restore") and callable(getattr(db_obj, "restore")):
            db_obj.restore()
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
        return None
    
    async def restore_by_id(self, id: int) -> Optional[ModelType]:
        """
        Khôi phục đối tượng theo ID
        """
        query = select(self.model).where(self.model.id == id)
        # Không lọc daXoa.is_(None) vì chúng ta muốn lấy cả bản ghi đã bị xóa
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            return None
            
        return await self.restore(db_obj=db_obj) 