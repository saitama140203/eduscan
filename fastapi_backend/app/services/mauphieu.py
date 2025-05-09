from typing import Optional, List, Dict, Any, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mauphieu import MauPhieuTraLoi
from app.schemas.mauphieu import MauPhieuTraLoiCreate, MauPhieuTraLoiUpdate
from app.services.base import BaseService


class MauPhieuTraLoiService(BaseService[MauPhieuTraLoi, MauPhieuTraLoiCreate, MauPhieuTraLoiUpdate]):
    """
    Service xử lý logic liên quan đến mẫu phiếu trả lời
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, MauPhieuTraLoi)
    
    async def get_by_tochuc(self, tochuc_id: int) -> List[MauPhieuTraLoi]:
        """
        Lấy danh sách mẫu phiếu trả lời theo tổ chức
        """
        stmt = select(MauPhieuTraLoi).where(MauPhieuTraLoi.maToChuc == tochuc_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_macdinh_by_tochuc(self, tochuc_id: int) -> Optional[MauPhieuTraLoi]:
        """
        Lấy mẫu phiếu trả lời mặc định của tổ chức
        """
        stmt = select(MauPhieuTraLoi).where(
            MauPhieuTraLoi.maToChuc == tochuc_id,
            MauPhieuTraLoi.laMacDinh == True
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, obj_in: MauPhieuTraLoiCreate) -> MauPhieuTraLoi:
        """
        Tạo mẫu phiếu trả lời mới
        """
        db_obj = MauPhieuTraLoi(
            maToChuc=obj_in.to_chuc_id,
            maNguoiTao=obj_in.nguoi_tao_id,
            tenMauPhieu=obj_in.ten,
            soCauHoi=obj_in.cau_hinh.get("soCauHoi", 40) if obj_in.cau_hinh else 40,
            soLuaChonMoiCau=obj_in.cau_hinh.get("soLuaChonMoiCau", 4) if obj_in.cau_hinh else 4,
            khoGiay=obj_in.cau_hinh.get("khoGiay", "A4") if obj_in.cau_hinh else "A4",
            coTuLuan=obj_in.cau_hinh.get("coTuLuan", False) if obj_in.cau_hinh else False,
            coThongTinHocSinh=obj_in.cau_hinh.get("coThongTinHocSinh", True) if obj_in.cau_hinh else True,
            coLogo=obj_in.cau_hinh.get("coLogo", False) if obj_in.cau_hinh else False,
            cauTrucJSON=obj_in.cau_hinh,
            laMacDinh=obj_in.cau_hinh.get("laMacDinh", False) if obj_in.cau_hinh else False,
            laCongKhai=obj_in.cau_hinh.get("laCongKhai", False) if obj_in.cau_hinh else False,
        )
        
        # Nếu là mẫu mặc định, bỏ tất cả mẫu mặc định khác của tổ chức
        if db_obj.laMacDinh:
            await self._remove_old_default(db_obj.maToChuc)
            
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        *,
        db_obj: MauPhieuTraLoi,
        obj_in: Union[MauPhieuTraLoiUpdate, Dict[str, Any]]
    ) -> MauPhieuTraLoi:
        """
        Cập nhật thông tin mẫu phiếu trả lời
        """
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        # Xử lý cấu hình
        if "cau_hinh" in update_data and update_data["cau_hinh"]:
            cau_hinh = update_data.pop("cau_hinh")
            
            if "soCauHoi" in cau_hinh:
                db_obj.soCauHoi = cau_hinh["soCauHoi"]
                
            if "soLuaChonMoiCau" in cau_hinh:
                db_obj.soLuaChonMoiCau = cau_hinh["soLuaChonMoiCau"]
                
            if "khoGiay" in cau_hinh:
                db_obj.khoGiay = cau_hinh["khoGiay"]
                
            if "coTuLuan" in cau_hinh:
                db_obj.coTuLuan = cau_hinh["coTuLuan"]
                
            if "coThongTinHocSinh" in cau_hinh:
                db_obj.coThongTinHocSinh = cau_hinh["coThongTinHocSinh"]
                
            if "coLogo" in cau_hinh:
                db_obj.coLogo = cau_hinh["coLogo"]
                
            if "laMacDinh" in cau_hinh:
                old_default = db_obj.laMacDinh
                db_obj.laMacDinh = cau_hinh["laMacDinh"]
                
                # Nếu đang set làm mặc định, bỏ tất cả mẫu mặc định khác
                if not old_default and db_obj.laMacDinh:
                    await self._remove_old_default(db_obj.maToChuc, exclude_id=db_obj.id)
                    
            if "laCongKhai" in cau_hinh:
                db_obj.laCongKhai = cau_hinh["laCongKhai"]
                
            # Cập nhật cấu trúc JSON
            db_obj.cauTrucJSON = {**db_obj.cauTrucJSON, **cau_hinh} if db_obj.cauTrucJSON else cau_hinh
        
        # Cập nhật các trường khác
        if "ten" in update_data:
            db_obj.tenMauPhieu = update_data["ten"]
            
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def _remove_old_default(self, tochuc_id: int, exclude_id: Optional[int] = None) -> None:
        """
        Bỏ tất cả mẫu phiếu mặc định khác của tổ chức
        """
        query = select(MauPhieuTraLoi).where(
            MauPhieuTraLoi.maToChuc == tochuc_id,
            MauPhieuTraLoi.laMacDinh == True
        )
        
        if exclude_id:
            query = query.where(MauPhieuTraLoi.id != exclude_id)
            
        result = await self.db.execute(query)
        old_defaults = result.scalars().all()
        
        for old_default in old_defaults:
            old_default.laMacDinh = False
            self.db.add(old_default)
        
        await self.db.commit() 