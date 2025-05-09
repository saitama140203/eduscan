from typing import Optional, List, Dict, Any, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.hocsinh import HocSinh
from app.schemas.hocsinh import HocSinhCreate, HocSinhUpdate
from app.services.base import BaseService


class HocSinhService(BaseService[HocSinh, HocSinhCreate, HocSinhUpdate]):
    """
    Service xử lý logic liên quan đến học sinh
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, HocSinh)
    
    async def get_by_id_with_relationships(self, id: int) -> Optional[HocSinh]:
        """
        Lấy thông tin học sinh theo ID kèm theo các mối quan hệ
        """
        stmt = select(HocSinh).where(
            HocSinh.id == id
        ).options(
            joinedload(HocSinh.lopHoc)
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_lop_hoc(self, lop_hoc_id: int) -> List[HocSinh]:
        """
        Lấy danh sách học sinh theo lớp học
        """
        stmt = select(HocSinh).where(
            HocSinh.maLopHoc == lop_hoc_id
        ).order_by(
            HocSinh.hoTen
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_by_ma_hoc_sinh_truong(self, ma_hoc_sinh_truong: str, lop_hoc_id: int = None) -> Optional[HocSinh]:
        """
        Lấy học sinh theo mã học sinh trường
        """
        stmt = select(HocSinh).where(
            HocSinh.maHocSinhTruong == ma_hoc_sinh_truong
        )
        
        if lop_hoc_id:
            stmt = stmt.where(HocSinh.maLopHoc == lop_hoc_id)
            
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi_with_relationships(
        self, *, skip: int = 0, limit: int = 100, **filters
    ) -> List[HocSinh]:
        """
        Lấy danh sách học sinh với các mối quan hệ
        """
        query = select(HocSinh).options(
            joinedload(HocSinh.lopHoc)
        )
        
        # Áp dụng các bộ lọc nếu có
        for field, value in filters.items():
            if hasattr(HocSinh, field) and value is not None:
                query = query.where(getattr(HocSinh, field) == value)
        
        # Thêm phân trang
        query = query.offset(skip).limit(limit).order_by(HocSinh.hoTen)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, obj_in: HocSinhCreate) -> HocSinh:
        """
        Tạo học sinh mới
        """
        # Kiểm tra xem mã học sinh đã tồn tại trong lớp chưa
        existing = await self.get_by_ma_hoc_sinh_truong(
            obj_in.maHocSinhTruong, 
            obj_in.maLopHoc
        )
        
        if existing:
            # Nếu đã tồn tại, có thể cập nhật hoặc bỏ qua
            # Ở đây chúng ta trả về học sinh đã tồn tại
            return existing
        
        db_obj = HocSinh(
            maLopHoc=obj_in.maLopHoc,
            maHocSinhTruong=obj_in.maHocSinhTruong,
            hoTen=obj_in.hoTen,
            ngaySinh=obj_in.ngaySinh,
            gioiTinh=obj_in.gioiTinh.value if obj_in.gioiTinh else None,
            soDienThoaiPhuHuynh=obj_in.soDienThoaiPhuHuynh,
            emailPhuHuynh=obj_in.emailPhuHuynh,
            trangThai=obj_in.trangThai
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        *,
        db_obj: HocSinh,
        obj_in: Union[HocSinhUpdate, Dict[str, Any]]
    ) -> HocSinh:
        """
        Cập nhật thông tin học sinh
        """
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        # Cập nhật các trường
        if "maLopHoc" in update_data:
            db_obj.maLopHoc = update_data["maLopHoc"]
            
        if "maHocSinhTruong" in update_data:
            # Kiểm tra xem mã học sinh mới đã tồn tại trong lớp chưa
            if update_data["maHocSinhTruong"] != db_obj.maHocSinhTruong:
                existing = await self.get_by_ma_hoc_sinh_truong(
                    update_data["maHocSinhTruong"], 
                    update_data.get("maLopHoc", db_obj.maLopHoc)
                )
                if existing:
                    # Nếu đã tồn tại, không cho phép cập nhật thành mã đã tồn tại
                    # Có thể xử lý tùy theo yêu cầu của ứng dụng
                    # Ở đây ta giữ nguyên mã cũ
                    pass
                else:
                    db_obj.maHocSinhTruong = update_data["maHocSinhTruong"]
            
        if "hoTen" in update_data:
            db_obj.hoTen = update_data["hoTen"]
            
        if "ngaySinh" in update_data:
            db_obj.ngaySinh = update_data["ngaySinh"]
            
        if "gioiTinh" in update_data:
            db_obj.gioiTinh = update_data["gioiTinh"].value if update_data["gioiTinh"] else None
            
        if "soDienThoaiPhuHuynh" in update_data:
            db_obj.soDienThoaiPhuHuynh = update_data["soDienThoaiPhuHuynh"]
            
        if "emailPhuHuynh" in update_data:
            db_obj.emailPhuHuynh = update_data["emailPhuHuynh"]
            
        if "trangThai" in update_data:
            db_obj.trangThai = update_data["trangThai"]
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def bulk_create_from_list(self, hoc_sinh_list: List[HocSinhCreate]) -> List[HocSinh]:
        """
        Tạo nhiều học sinh từ danh sách
        """
        result = []
        
        for hoc_sinh_data in hoc_sinh_list:
            # Kiểm tra xem học sinh đã tồn tại chưa
            existing = await self.get_by_ma_hoc_sinh_truong(
                hoc_sinh_data.maHocSinhTruong, 
                hoc_sinh_data.maLopHoc
            )
            
            if existing:
                # Nếu đã tồn tại, thêm vào kết quả
                result.append(existing)
                continue
            
            # Nếu chưa tồn tại, tạo mới
            db_obj = HocSinh(
                maLopHoc=hoc_sinh_data.maLopHoc,
                maHocSinhTruong=hoc_sinh_data.maHocSinhTruong,
                hoTen=hoc_sinh_data.hoTen,
                ngaySinh=hoc_sinh_data.ngaySinh,
                gioiTinh=hoc_sinh_data.gioiTinh.value if hoc_sinh_data.gioiTinh else None,
                soDienThoaiPhuHuynh=hoc_sinh_data.soDienThoaiPhuHuynh,
                emailPhuHuynh=hoc_sinh_data.emailPhuHuynh,
                trangThai=hoc_sinh_data.trangThai
            )
            
            self.db.add(db_obj)
            # Không commit ở đây để tạo bulk insert
        
        # Commit một lần sau khi tạo tất cả
        await self.db.commit()
        
        # Refresh tất cả các đối tượng
        for db_obj in self.db.new:
            if isinstance(db_obj, HocSinh):
                await self.db.refresh(db_obj)
                result.append(db_obj)
        
        return result
    
    async def search_hoc_sinh(self, term: str, lop_hoc_id: int = None) -> List[HocSinh]:
        """
        Tìm kiếm học sinh theo tên hoặc mã học sinh
        """
        search_term = f"%{term}%"
        
        query = select(HocSinh).where(
            (HocSinh.hoTen.ilike(search_term)) |
            (HocSinh.maHocSinhTruong.ilike(search_term))
        )
        
        if lop_hoc_id is not None:
            query = query.where(HocSinh.maLopHoc == lop_hoc_id)
            
        query = query.order_by(HocSinh.hoTen)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def chuyen_lop(self, hoc_sinh_id: int, lop_hoc_moi_id: int) -> Optional[HocSinh]:
        """
        Chuyển học sinh sang lớp mới
        """
        hoc_sinh = await self.get_by_id(hoc_sinh_id)
        if not hoc_sinh:
            return None
        
        # Lưu lại mã học sinh trường để kiểm tra trùng lặp
        ma_hoc_sinh_truong = hoc_sinh.maHocSinhTruong
        
        # Kiểm tra xem mã học sinh đã tồn tại trong lớp mới chưa
        existing = await self.get_by_ma_hoc_sinh_truong(ma_hoc_sinh_truong, lop_hoc_moi_id)
        if existing:
            # Nếu đã tồn tại, không cho phép chuyển
            # Có thể xử lý tùy theo yêu cầu của ứng dụng
            return None
        
        # Cập nhật lớp học mới
        hoc_sinh.maLopHoc = lop_hoc_moi_id
        self.db.add(hoc_sinh)
        await self.db.commit()
        await self.db.refresh(hoc_sinh)
        
        return hoc_sinh 