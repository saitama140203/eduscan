from typing import Optional, List, Dict, Any, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.baikiemtra import BaiKiemTra, DapAn, BaiKiemTraLopHoc
from app.schemas.baikiemtra import (
    BaiKiemTraCreate, 
    BaiKiemTraUpdate, 
    DapAnCreate, 
    DapAnUpdate,
    BaiKiemTraWithLopHoc
)
from app.services.base import BaseService


class BaiKiemTraService(BaseService[BaiKiemTra, BaiKiemTraCreate, BaiKiemTraUpdate]):
    """
    Service xử lý logic liên quan đến bài kiểm tra
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, BaiKiemTra)
    
    async def get_by_tochuc(self, tochuc_id: int) -> List[BaiKiemTra]:
        """
        Lấy danh sách bài kiểm tra theo tổ chức
        """
        stmt = select(BaiKiemTra).where(BaiKiemTra.maToChuc == tochuc_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create(self, obj_in: BaiKiemTraCreate) -> BaiKiemTra:
        """
        Tạo bài kiểm tra mới
        """
        db_obj = BaiKiemTra(
            maToChuc=obj_in.to_chuc_id,
            maNguoiTao=obj_in.nguoi_tao_id,
            maMauPhieu=obj_in.mau_phieu_id,
            tieuDe=obj_in.ten,
            monHoc=obj_in.mo_ta or "Chưa xác định",
            thoiGianLamBai=obj_in.thoi_gian_lam_bai or 0,
            tongSoCau=0,  # Sẽ cập nhật sau khi thêm đáp án
            tongDiem=10.0,  # Mặc định 10 điểm
            moTa=obj_in.mo_ta,
            trangThai=obj_in.trang_thai.value if obj_in.trang_thai else "draft"
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def get_with_lop_hoc(self, id: int) -> Optional[BaiKiemTraWithLopHoc]:
        """
        Lấy thông tin bài kiểm tra cùng với danh sách lớp học được gán
        """
        # Lấy bài kiểm tra
        stmt = select(BaiKiemTra).where(BaiKiemTra.id == id)
        result = await self.db.execute(stmt)
        bai_kiem_tra = result.scalar_one_or_none()
        
        if not bai_kiem_tra:
            return None
        
        # Lấy danh sách lớp học được gán
        stmt = select(BaiKiemTraLopHoc).where(BaiKiemTraLopHoc.maBaiKiemTra == id)
        result = await self.db.execute(stmt)
        lop_hoc_links = result.scalars().all()
        
        # Chuyển đổi sang BaiKiemTraWithLopHoc schema
        bai_kiem_tra_with_lop_hoc = BaiKiemTraWithLopHoc(
            id=bai_kiem_tra.id,
            ten=bai_kiem_tra.tieuDe,
            mo_ta=bai_kiem_tra.moTa,
            thoi_gian_lam_bai=bai_kiem_tra.thoiGianLamBai,
            to_chuc_id=bai_kiem_tra.maToChuc,
            nguoi_tao_id=bai_kiem_tra.maNguoiTao,
            mau_phieu_id=bai_kiem_tra.maMauPhieu,
            trang_thai=bai_kiem_tra.trangThai,
            created_at=bai_kiem_tra.thoiGianTao.isoformat() if bai_kiem_tra.thoiGianTao else None,
            updated_at=bai_kiem_tra.thoiGianCapNhat.isoformat() if bai_kiem_tra.thoiGianCapNhat else None,
            lop_hoc_ids=[link.maLopHoc for link in lop_hoc_links]
        )
        
        return bai_kiem_tra_with_lop_hoc
    
    async def update(
        self,
        *,
        db_obj: BaiKiemTra,
        obj_in: Union[BaiKiemTraUpdate, Dict[str, Any]]
    ) -> BaiKiemTra:
        """
        Cập nhật thông tin bài kiểm tra
        """
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        # Cập nhật các trường
        if "ten" in update_data:
            db_obj.tieuDe = update_data["ten"]
            
        if "mo_ta" in update_data:
            db_obj.moTa = update_data["mo_ta"]
            
        if "thoi_gian_lam_bai" in update_data:
            db_obj.thoiGianLamBai = update_data["thoi_gian_lam_bai"]
            
        if "mau_phieu_id" in update_data:
            db_obj.maMauPhieu = update_data["mau_phieu_id"]
            
        if "trang_thai" in update_data:
            db_obj.trangThai = update_data["trang_thai"].value if hasattr(update_data["trang_thai"], "value") else update_data["trang_thai"]
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def assign_to_lop_hoc(self, bai_kiem_tra_id: int, lop_hoc_id: int) -> BaiKiemTraLopHoc:
        """
        Gán bài kiểm tra cho lớp học
        """
        # Kiểm tra xem liên kết đã tồn tại chưa
        stmt = select(BaiKiemTraLopHoc).where(
            BaiKiemTraLopHoc.maBaiKiemTra == bai_kiem_tra_id,
            BaiKiemTraLopHoc.maLopHoc == lop_hoc_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        
        # Tạo liên kết mới
        db_obj = BaiKiemTraLopHoc(
            maBaiKiemTra=bai_kiem_tra_id,
            maLopHoc=lop_hoc_id
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def unassign_from_lop_hoc(self, bai_kiem_tra_id: int, lop_hoc_id: int) -> bool:
        """
        Hủy gán bài kiểm tra khỏi lớp học
        """
        stmt = select(BaiKiemTraLopHoc).where(
            BaiKiemTraLopHoc.maBaiKiemTra == bai_kiem_tra_id,
            BaiKiemTraLopHoc.maLopHoc == lop_hoc_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if not existing:
            return False
        
        await self.db.delete(existing)
        await self.db.commit()
        return True


class DapAnService(BaseService[DapAn, DapAnCreate, DapAnUpdate]):
    """
    Service xử lý logic liên quan đến đáp án
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, DapAn)
    
    async def get_by_bai_kiem_tra(self, bai_kiem_tra_id: int) -> Optional[DapAn]:
        """
        Lấy đáp án theo bài kiểm tra
        """
        stmt = select(DapAn).where(DapAn.maBaiKiemTra == bai_kiem_tra_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, obj_in: DapAnCreate) -> DapAn:
        """
        Tạo đáp án mới cho bài kiểm tra
        """
        # Kiểm tra xem bài kiểm tra đã có đáp án chưa
        existing = await self.get_by_bai_kiem_tra(obj_in.bai_kiem_tra_id)
        if existing:
            # Nếu đã có đáp án, cập nhật đáp án hiện tại
            return await self.update(db_obj=existing, obj_in=obj_in)
        
        # Tạo cấu trúc JSON cho đáp án
        dap_an_json = {
            "cauHoi": obj_in.cau_hoi,
            "luaChon": obj_in.lua_chon or {},
            "dapAn": obj_in.dap_an_dung
        }
        
        # Tạo cấu trúc JSON cho điểm của từng câu
        diem_moi_cau_json = {
            "diem": obj_in.diem or 1.0
        }
        
        db_obj = DapAn(
            maBaiKiemTra=obj_in.bai_kiem_tra_id,
            dapAnJSON=dap_an_json,
            diemMoiCauJSON=diem_moi_cau_json
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        # Cập nhật tổng số câu và tổng điểm trong bài kiểm tra
        await self._update_bai_kiem_tra_info(db_obj)
        
        return db_obj
    
    async def update(
        self,
        *,
        db_obj: DapAn,
        obj_in: Union[DapAnUpdate, Dict[str, Any]]
    ) -> DapAn:
        """
        Cập nhật thông tin đáp án
        """
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        # Cập nhật JSON đáp án
        if db_obj.dapAnJSON is None:
            db_obj.dapAnJSON = {}
            
        if "cau_hoi" in update_data:
            db_obj.dapAnJSON["cauHoi"] = update_data["cau_hoi"]
            
        if "lua_chon" in update_data:
            db_obj.dapAnJSON["luaChon"] = update_data["lua_chon"]
            
        if "dap_an_dung" in update_data:
            db_obj.dapAnJSON["dapAn"] = update_data["dap_an_dung"]
        
        # Cập nhật JSON điểm
        if db_obj.diemMoiCauJSON is None:
            db_obj.diemMoiCauJSON = {}
            
        if "diem" in update_data:
            db_obj.diemMoiCauJSON["diem"] = update_data["diem"]
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        # Cập nhật thông tin bài kiểm tra
        await self._update_bai_kiem_tra_info(db_obj)
        
        return db_obj
    
    async def _update_bai_kiem_tra_info(self, dap_an: DapAn) -> None:
        """
        Cập nhật thông tin tổng số câu và tổng điểm trong bài kiểm tra
        """
        bai_kiem_tra_service = BaiKiemTraService(self.db)
        bai_kiem_tra = await bai_kiem_tra_service.get_by_id(dap_an.maBaiKiemTra)
        
        if bai_kiem_tra and dap_an.dapAnJSON:
            # Tính tổng số câu từ đáp án
            so_cau = 1  # Mặc định là 1 câu
            
            # Tính tổng điểm từ điểm mỗi câu
            tong_diem = dap_an.diemMoiCauJSON.get("diem", 1.0) if dap_an.diemMoiCauJSON else 1.0
            
            # Cập nhật bài kiểm tra
            bai_kiem_tra.tongSoCau = so_cau
            bai_kiem_tra.tongDiem = tong_diem
            self.db.add(bai_kiem_tra)
            await self.db.commit() 