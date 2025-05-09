from typing import Optional, List, Dict, Any, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.lophoc import LopHoc
from app.schemas.lophoc import LopHocCreate, LopHocUpdate
from app.services.base import BaseService


class LopHocService(BaseService[LopHoc, LopHocCreate, LopHocUpdate]):
    """
    Service xử lý logic liên quan đến lớp học
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, LopHoc)
    
    async def get_by_id_with_relationships(self, id: int) -> Optional[LopHoc]:
        """
        Lấy thông tin lớp học theo ID kèm theo các mối quan hệ
        """
        stmt = select(LopHoc).where(
            LopHoc.id == id
        ).options(
            joinedload(LopHoc.toChuc),
            joinedload(LopHoc.giaoVienChuNhiem),
            joinedload(LopHoc.hocSinhs)
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_to_chuc(self, to_chuc_id: int) -> List[LopHoc]:
        """
        Lấy danh sách lớp học theo tổ chức
        """
        stmt = select(LopHoc).where(
            LopHoc.maToChuc == to_chuc_id
        ).order_by(
            LopHoc.tenLop
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_by_giao_vien(self, giao_vien_id: int) -> List[LopHoc]:
        """
        Lấy danh sách lớp học theo giáo viên chủ nhiệm
        """
        stmt = select(LopHoc).where(
            LopHoc.maGiaoVienChuNhiem == giao_vien_id
        ).order_by(
            LopHoc.tenLop
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_multi_with_relationships(
        self, *, skip: int = 0, limit: int = 100, **filters
    ) -> List[LopHoc]:
        """
        Lấy danh sách lớp học với các mối quan hệ
        """
        query = select(LopHoc).options(
            joinedload(LopHoc.toChuc),
            joinedload(LopHoc.giaoVienChuNhiem)
        )
        
        # Áp dụng các bộ lọc nếu có
        for field, value in filters.items():
            if hasattr(LopHoc, field) and value is not None:
                query = query.where(getattr(LopHoc, field) == value)
        
        # Thêm phân trang
        query = query.offset(skip).limit(limit).order_by(LopHoc.tenLop)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, obj_in: LopHocCreate) -> LopHoc:
        """
        Tạo lớp học mới
        """
        db_obj = LopHoc(
            maToChuc=obj_in.maToChuc,
            tenLop=obj_in.tenLop,
            capHoc=obj_in.capHoc,
            namHoc=obj_in.namHoc,
            maGiaoVienChuNhiem=obj_in.maGiaoVienChuNhiem,
            moTa=obj_in.moTa,
            trangThai=obj_in.trangThai
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        *,
        db_obj: LopHoc,
        obj_in: Union[LopHocUpdate, Dict[str, Any]]
    ) -> LopHoc:
        """
        Cập nhật thông tin lớp học
        """
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        # Cập nhật các trường
        if "tenLop" in update_data:
            db_obj.tenLop = update_data["tenLop"]
            
        if "capHoc" in update_data:
            db_obj.capHoc = update_data["capHoc"]
            
        if "namHoc" in update_data:
            db_obj.namHoc = update_data["namHoc"]
            
        if "maGiaoVienChuNhiem" in update_data:
            db_obj.maGiaoVienChuNhiem = update_data["maGiaoVienChuNhiem"]
            
        if "moTa" in update_data:
            db_obj.moTa = update_data["moTa"]
            
        if "trangThai" in update_data:
            db_obj.trangThai = update_data["trangThai"]
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def is_lop_hoc_in_to_chuc(self, lop_hoc_id: int, to_chuc_id: int) -> bool:
        """
        Kiểm tra xem lớp học có thuộc tổ chức không
        """
        lop_hoc = await self.get_by_id(lop_hoc_id)
        return lop_hoc is not None and lop_hoc.maToChuc == to_chuc_id 