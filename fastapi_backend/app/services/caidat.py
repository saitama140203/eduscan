from typing import Optional, List, Dict, Any, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.caidat import CaiDat, TapTin
from app.schemas.caidat import CaiDatCreate, CaiDatUpdate
from app.schemas.taptin import TapTinCreate, TapTinUpdate
from app.services.base import BaseService


class CaiDatService(BaseService[CaiDat, CaiDatCreate, CaiDatUpdate]):
    """
    Service xử lý logic liên quan đến cài đặt
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, CaiDat)
    
    async def get_by_to_chuc_va_tu_khoa(
        self, to_chuc_id: int, tu_khoa: str
    ) -> Optional[CaiDat]:
        """
        Lấy cài đặt theo tổ chức và từ khóa
        """
        stmt = select(CaiDat).where(
            CaiDat.maToChuc == to_chuc_id,
            CaiDat.tuKhoa == tu_khoa
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_by_to_chuc(self, to_chuc_id: int) -> List[CaiDat]:
        """
        Lấy tất cả cài đặt của một tổ chức
        """
        stmt = select(CaiDat).where(
            CaiDat.maToChuc == to_chuc_id
        ).order_by(
            CaiDat.tuKhoa
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create(self, obj_in: CaiDatCreate) -> CaiDat:
        """
        Tạo cài đặt mới
        """
        # Kiểm tra xem cài đặt đã tồn tại chưa
        existing = await self.get_by_to_chuc_va_tu_khoa(
            obj_in.to_chuc_id, 
            obj_in.ten_cai_dat
        )
        
        if existing:
            # Nếu đã tồn tại, cập nhật cài đặt hiện tại
            return await self.update(db_obj=existing, obj_in=obj_in)
        
        # Chuyển đổi giữa schema và model field names
        db_obj = CaiDat(
            maToChuc=obj_in.to_chuc_id,
            tuKhoa=obj_in.ten_cai_dat,
            giaTri=obj_in.gia_tri if hasattr(obj_in, 'gia_tri') else None
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        *,
        db_obj: CaiDat,
        obj_in: Union[CaiDatUpdate, Dict[str, Any]]
    ) -> CaiDat:
        """
        Cập nhật thông tin cài đặt
        """
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        # Cập nhật các trường
        if "gia_tri" in update_data:
            db_obj.giaTri = update_data["gia_tri"]
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def upsert(
        self, to_chuc_id: int, tu_khoa: str, gia_tri: Any
    ) -> CaiDat:
        """
        Cập nhật hoặc tạo mới cài đặt
        """
        cai_dat = await self.get_by_to_chuc_va_tu_khoa(to_chuc_id, tu_khoa)
        
        if cai_dat:
            # Nếu đã tồn tại, cập nhật giá trị
            cai_dat.giaTri = gia_tri
            self.db.add(cai_dat)
            await self.db.commit()
            await self.db.refresh(cai_dat)
            return cai_dat
        else:
            # Nếu chưa tồn tại, tạo mới
            db_obj = CaiDat(
                maToChuc=to_chuc_id,
                tuKhoa=tu_khoa,
                giaTri=gia_tri
            )
            
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj


class TapTinService(BaseService[TapTin, TapTinCreate, TapTinUpdate]):
    """
    Service xử lý logic liên quan đến tập tin
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, TapTin)
    
    async def get_by_to_chuc(self, to_chuc_id: int) -> List[TapTin]:
        """
        Lấy danh sách tập tin theo tổ chức
        """
        stmt = select(TapTin).where(
            TapTin.maToChuc == to_chuc_id
        ).order_by(
            TapTin.thoiGianTao.desc()
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_by_nguoi_dung(self, nguoi_dung_id: int) -> List[TapTin]:
        """
        Lấy danh sách tập tin theo người dùng
        """
        stmt = select(TapTin).where(
            TapTin.maNguoiDung == nguoi_dung_id
        ).order_by(
            TapTin.thoiGianTao.desc()
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_by_thuc_the(
        self, thuc_the_nguon: str, ma_thuc_the_nguon: int
    ) -> List[TapTin]:
        """
        Lấy danh sách tập tin theo thực thể nguồn
        """
        stmt = select(TapTin).where(
            TapTin.thucTheNguon == thuc_the_nguon,
            TapTin.maThucTheNguon == ma_thuc_the_nguon
        ).order_by(
            TapTin.thoiGianTao.desc()
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create(self, obj_in: TapTinCreate) -> TapTin:
        """
        Tạo tập tin mới
        """
        db_obj = TapTin(
            maNguoiDung=obj_in.nguoi_dung_id,
            maToChuc=obj_in.to_chuc_id,
            tenTapTin=obj_in.ten_tap_tin,
            duongDan=obj_in.duong_dan,
            loaiTapTin=obj_in.loai_tap_tin,
            kichThuoc=obj_in.kich_thuoc,
            thucTheNguon=obj_in.thuc_the_nguon,
            maThucTheNguon=obj_in.ma_thuc_the_nguon
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete_by_thuc_the(
        self, thuc_the_nguon: str, ma_thuc_the_nguon: int
    ) -> int:
        """
        Xóa tất cả tập tin của một thực thể
        """
        # Lấy danh sách các tập tin cần xóa
        files = await self.get_by_thuc_the(thuc_the_nguon, ma_thuc_the_nguon)
        
        count = 0
        for file in files:
            await self.db.delete(file)
            count += 1
            
        if count > 0:
            await self.db.commit()
            
        return count 