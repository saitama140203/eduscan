from typing import Optional, List, Dict, Any, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tochuc import ToChuc
from app.schemas.tochuc import ToChucCreate, ToChucUpdate
from app.services.base import BaseService


class ToChucService(BaseService[ToChuc, ToChucCreate, ToChucUpdate]):
    """
    Service xử lý logic liên quan đến tổ chức
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ToChuc)
    
    async def get_by_id_with_relationships(self, id: int) -> Optional[ToChuc]:
        """
        Lấy thông tin tổ chức theo ID kèm theo các mối quan hệ
        """
        stmt = select(ToChuc).where(
            ToChuc.id == id
        ).options(
            selectinload(ToChuc.nguoiDungs),
            selectinload(ToChuc.lopHocs),
            selectinload(ToChuc.caiDats)
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_ten(self, ten_to_chuc: str) -> Optional[ToChuc]:
        """
        Lấy tổ chức theo tên tổ chức
        """
        stmt = select(ToChuc).where(
            ToChuc.tenToChuc == ten_to_chuc
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_loai(self, loai_to_chuc: str) -> List[ToChuc]:
        """
        Lấy danh sách tổ chức theo loại
        """
        stmt = select(ToChuc).where(
            ToChuc.loaiToChuc == loai_to_chuc
        ).order_by(
            ToChuc.tenToChuc
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create(self, obj_in: ToChucCreate) -> ToChuc:
        """
        Tạo tổ chức mới
        """
        db_obj = ToChuc(
            tenToChuc=obj_in.tenToChuc,
            loaiToChuc=obj_in.loaiToChuc.value if hasattr(obj_in.loaiToChuc, 'value') else obj_in.loaiToChuc,
            diaChi=obj_in.diaChi,
            urlLogo=obj_in.urlLogo
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        *,
        db_obj: ToChuc,
        obj_in: Union[ToChucUpdate, Dict[str, Any]]
    ) -> ToChuc:
        """
        Cập nhật thông tin tổ chức
        """
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        # Cập nhật các trường
        if "tenToChuc" in update_data:
            db_obj.tenToChuc = update_data["tenToChuc"]
            
        if "loaiToChuc" in update_data:
            db_obj.loaiToChuc = update_data["loaiToChuc"].value if hasattr(update_data["loaiToChuc"], 'value') else update_data["loaiToChuc"]
            
        if "diaChi" in update_data:
            db_obj.diaChi = update_data["diaChi"]
            
        if "urlLogo" in update_data:
            db_obj.urlLogo = update_data["urlLogo"]
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def search_to_chuc(self, term: str) -> List[ToChuc]:
        """
        Tìm kiếm tổ chức theo tên hoặc địa chỉ
        """
        search_term = f"%{term}%"
        
        stmt = select(ToChuc).where(
            (ToChuc.tenToChuc.ilike(search_term)) |
            (ToChuc.diaChi.ilike(search_term))
        ).order_by(
            ToChuc.tenToChuc
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all() 