from typing import Optional, List, Dict, Any, Union, Tuple
from decimal import Decimal

from sqlalchemy import select, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.phieutraloi import PhieuTraLoi, KetQua, ThongKeKiemTra
from app.models.hocsinh import HocSinh
from app.schemas.phieutraloi import (
    PhieuTraLoiCreate, 
    PhieuTraLoiUpdate, 
    KetQuaCreate, 
    KetQuaUpdate,
    ThongKeKiemTraCreate,
    KetQuaHocSinhResponse,
    ThongKeResponse
)
from app.services.base import BaseService


class PhieuTraLoiService(BaseService[PhieuTraLoi, PhieuTraLoiCreate, PhieuTraLoiUpdate]):
    """
    Service xử lý logic liên quan đến phiếu trả lời
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, PhieuTraLoi)
    
    async def get_by_hoc_sinh_va_bai_kiem_tra(
        self, hoc_sinh_id: int, bai_kiem_tra_id: int
    ) -> Optional[PhieuTraLoi]:
        """
        Lấy phiếu trả lời theo học sinh và bài kiểm tra
        """
        stmt = select(PhieuTraLoi).where(
            PhieuTraLoi.maHocSinh == hoc_sinh_id,
            PhieuTraLoi.maBaiKiemTra == bai_kiem_tra_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_phieu_tra_loi_chua_xu_ly(self, to_chuc_id: int) -> List[PhieuTraLoi]:
        """
        Lấy danh sách phiếu trả lời chưa được xử lý hoàn tất của tổ chức
        """
        stmt = select(PhieuTraLoi).join(
            PhieuTraLoi.baiKiemTra
        ).where(
            PhieuTraLoi.daXuLyHoanTat == False,
            PhieuTraLoi.baiKiemTra.has(maToChuc=to_chuc_id)
        ).order_by(PhieuTraLoi.thoiGianTao.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create(self, obj_in: PhieuTraLoiCreate) -> PhieuTraLoi:
        """
        Tạo phiếu trả lời mới
        """
        db_obj = PhieuTraLoi(
            maBaiKiemTra=obj_in.bai_kiem_tra_id,
            maHocSinh=obj_in.hoc_sinh_id,
            maNguoiQuet=obj_in.nguoi_quet_id,
            urlHinhAnh=obj_in.url_hinh_anh,
            urlHinhAnhXuLy=obj_in.url_hinh_anh_xu_ly,
            cauTraLoiJSON=obj_in.cau_tra_loi,
            daXuLyHoanTat=obj_in.da_xu_ly_hoan_tat if hasattr(obj_in, 'da_xu_ly_hoan_tat') else False,
            doTinCay=obj_in.do_tin_cay if hasattr(obj_in, 'do_tin_cay') else None,
            canhBaoJSON=obj_in.canh_bao if hasattr(obj_in, 'canh_bao') else None
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        *,
        db_obj: PhieuTraLoi,
        obj_in: Union[PhieuTraLoiUpdate, Dict[str, Any]]
    ) -> PhieuTraLoi:
        """
        Cập nhật thông tin phiếu trả lời
        """
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        # Cập nhật các trường
        if "url_hinh_anh" in update_data:
            db_obj.urlHinhAnh = update_data["url_hinh_anh"]
            
        if "url_hinh_anh_xu_ly" in update_data:
            db_obj.urlHinhAnhXuLy = update_data["url_hinh_anh_xu_ly"]
            
        if "cau_tra_loi" in update_data:
            db_obj.cauTraLoiJSON = update_data["cau_tra_loi"]
            
        if "da_xu_ly_hoan_tat" in update_data:
            db_obj.daXuLyHoanTat = update_data["da_xu_ly_hoan_tat"]
            
        if "do_tin_cay" in update_data:
            db_obj.doTinCay = update_data["do_tin_cay"]
            
        if "canh_bao" in update_data:
            db_obj.canhBaoJSON = update_data["canh_bao"]
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def get_danh_sach_theo_bai_kiem_tra(self, bai_kiem_tra_id: int) -> List[PhieuTraLoi]:
        """
        Lấy danh sách phiếu trả lời theo bài kiểm tra
        """
        stmt = select(PhieuTraLoi).where(
            PhieuTraLoi.maBaiKiemTra == bai_kiem_tra_id
        ).order_by(PhieuTraLoi.thoiGianTao.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_danh_sach_theo_lop_hoc(self, lop_hoc_id: int, bai_kiem_tra_id: int = None) -> List[PhieuTraLoi]:
        """
        Lấy danh sách phiếu trả lời theo lớp học và bài kiểm tra (tuỳ chọn)
        """
        stmt = select(PhieuTraLoi).join(
            PhieuTraLoi.hocSinh
        ).where(
            HocSinh.maLopHoc == lop_hoc_id
        )
        
        if bai_kiem_tra_id:
            stmt = stmt.where(PhieuTraLoi.maBaiKiemTra == bai_kiem_tra_id)
            
        stmt = stmt.order_by(PhieuTraLoi.thoiGianTao.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().all()


class KetQuaService(BaseService[KetQua, KetQuaCreate, KetQuaUpdate]):
    """
    Service xử lý logic liên quan đến kết quả kiểm tra
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, KetQua)
    
    async def get_by_phieu_tra_loi(self, phieu_tra_loi_id: int) -> Optional[KetQua]:
        """
        Lấy kết quả theo phiếu trả lời
        """
        stmt = select(KetQua).where(KetQua.maPhieuTraLoi == phieu_tra_loi_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, obj_in: KetQuaCreate) -> KetQua:
        """
        Tạo kết quả mới
        """
        db_obj = KetQua(
            maPhieuTraLoi=obj_in.phieu_tra_loi_id,
            maBaiKiemTra=obj_in.bai_kiem_tra_id,
            maHocSinh=obj_in.hoc_sinh_id,
            diem=obj_in.diem,
            soCauDung=obj_in.so_cau_dung,
            soCauSai=obj_in.so_cau_sai,
            soCauChuaTraLoi=obj_in.so_cau_chua_tra_loi,
            chiTietJSON=obj_in.chi_tiet,
            diemTheoMonJSON=obj_in.diem_theo_mon,
            thuHangTrongLop=None  # Sẽ tính toán sau
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        # Cập nhật xếp hạng trong lớp
        await self._update_xep_hang(db_obj)
        
        # Cập nhật thống kê kiểm tra
        await self._update_thong_ke(db_obj)
        
        return db_obj
    
    async def update(
        self,
        *,
        db_obj: KetQua,
        obj_in: Union[KetQuaUpdate, Dict[str, Any]]
    ) -> KetQua:
        """
        Cập nhật thông tin kết quả
        """
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        
        # Cập nhật các trường
        if "diem" in update_data:
            db_obj.diem = update_data["diem"]
            
        if "so_cau_dung" in update_data:
            db_obj.soCauDung = update_data["so_cau_dung"]
            
        if "so_cau_sai" in update_data:
            db_obj.soCauSai = update_data["so_cau_sai"]
            
        if "so_cau_chua_tra_loi" in update_data:
            db_obj.soCauChuaTraLoi = update_data["so_cau_chua_tra_loi"]
            
        if "chi_tiet" in update_data:
            db_obj.chiTietJSON = update_data["chi_tiet"]
            
        if "diem_theo_mon" in update_data:
            db_obj.diemTheoMonJSON = update_data["diem_theo_mon"]
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        # Cập nhật xếp hạng trong lớp
        await self._update_xep_hang(db_obj)
        
        # Cập nhật thống kê kiểm tra
        await self._update_thong_ke(db_obj)
        
        return db_obj
    
    async def get_ket_qua_theo_bai_kiem_tra(self, bai_kiem_tra_id: int) -> List[KetQua]:
        """
        Lấy danh sách kết quả theo bài kiểm tra
        """
        stmt = select(KetQua).where(
            KetQua.maBaiKiemTra == bai_kiem_tra_id
        ).order_by(KetQua.diem.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_ket_qua_theo_hoc_sinh(self, hoc_sinh_id: int) -> List[KetQua]:
        """
        Lấy danh sách kết quả theo học sinh
        """
        stmt = select(KetQua).where(
            KetQua.maHocSinh == hoc_sinh_id
        ).order_by(KetQua.thoiGianTao.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_ket_qua_hoc_sinh_response(
        self, bai_kiem_tra_id: int, lop_hoc_id: int
    ) -> List[KetQuaHocSinhResponse]:
        """
        Lấy danh sách kết quả học sinh theo định dạng phản hồi
        """
        # Lấy danh sách học sinh và kết quả
        stmt = select(
            HocSinh.id,
            HocSinh.hoTen,
            HocSinh.maHocSinh,
            KetQua.diem,
            KetQua.thoiGianTao,
            KetQua.id.isnot(None).label("daLam")
        ).outerjoin(
            KetQua, 
            (KetQua.maHocSinh == HocSinh.id) & 
            (KetQua.maBaiKiemTra == bai_kiem_tra_id)
        ).where(
            HocSinh.maLopHoc == lop_hoc_id
        ).order_by(
            desc("daLam"),
            desc(KetQua.diem),
            HocSinh.hoTen
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        # Chuyển đổi sang dạng KetQuaHocSinhResponse
        responses = []
        for row in rows:
            response = KetQuaHocSinhResponse(
                hoc_sinh_id=row.id,
                ho_ten=row.hoTen,
                ma_hoc_sinh=row.maHocSinh,
                diem=float(row.diem) if row.diem is not None else 0.0,
                thoi_gian_lam_bai=None,  # Không có thông tin này trong model
                trang_thai=row.daLam
            )
            responses.append(response)
        
        return responses
    
    async def _update_xep_hang(self, ket_qua: KetQua) -> None:
        """
        Cập nhật xếp hạng trong lớp
        """
        # Lấy lớp học của học sinh
        stmt = select(HocSinh.maLopHoc).where(HocSinh.id == ket_qua.maHocSinh)
        result = await self.db.execute(stmt)
        lop_hoc_id = result.scalar_one_or_none()
        
        if not lop_hoc_id:
            return
        
        # Lấy danh sách kết quả của bài kiểm tra theo lớp
        stmt = select(KetQua.id).join(
            HocSinh, KetQua.maHocSinh == HocSinh.id
        ).where(
            KetQua.maBaiKiemTra == ket_qua.maBaiKiemTra,
            HocSinh.maLopHoc == lop_hoc_id
        ).order_by(
            KetQua.diem.desc()
        )
        
        result = await self.db.execute(stmt)
        ket_qua_ids = result.scalars().all()
        
        # Tìm vị trí của kết quả hiện tại
        try:
            xep_hang = ket_qua_ids.index(ket_qua.id) + 1
        except ValueError:
            xep_hang = len(ket_qua_ids) + 1
        
        # Cập nhật xếp hạng
        ket_qua.thuHangTrongLop = xep_hang
        self.db.add(ket_qua)
        await self.db.commit()
    
    async def _update_thong_ke(self, ket_qua: KetQua) -> None:
        """
        Cập nhật thống kê kiểm tra
        """
        # Tìm lớp học của học sinh
        stmt = select(HocSinh.maLopHoc).where(HocSinh.id == ket_qua.maHocSinh)
        result = await self.db.execute(stmt)
        lop_hoc_id = result.scalar_one_or_none()
        
        if not lop_hoc_id:
            return
        
        # Tìm hoặc tạo thống kê kiểm tra
        thong_ke_service = ThongKeKiemTraService(self.db)
        thong_ke = await thong_ke_service.get_by_bai_kiem_tra_va_lop_hoc(
            ket_qua.maBaiKiemTra, lop_hoc_id
        )
        
        if not thong_ke:
            # Tạo thống kê mới
            thong_ke_data = ThongKeKiemTraCreate(
                bai_kiem_tra_id=ket_qua.maBaiKiemTra,
                lop_hoc_id=lop_hoc_id
            )
            thong_ke = await thong_ke_service.create(thong_ke_data)
        
        # Cập nhật thống kê kiểm tra
        await thong_ke_service.update_thong_ke(thong_ke.id)


class ThongKeKiemTraService(BaseService[ThongKeKiemTra, ThongKeKiemTraCreate, Any]):
    """
    Service xử lý logic liên quan đến thống kê kiểm tra
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ThongKeKiemTra)
    
    async def get_by_bai_kiem_tra_va_lop_hoc(
        self, bai_kiem_tra_id: int, lop_hoc_id: int
    ) -> Optional[ThongKeKiemTra]:
        """
        Lấy thống kê kiểm tra theo bài kiểm tra và lớp học
        """
        stmt = select(ThongKeKiemTra).where(
            ThongKeKiemTra.maBaiKiemTra == bai_kiem_tra_id,
            ThongKeKiemTra.maLopHoc == lop_hoc_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_thong_ke_response(
        self, bai_kiem_tra_id: int, lop_hoc_id: int
    ) -> ThongKeResponse:
        """
        Lấy thống kê kiểm tra theo định dạng phản hồi
        """
        thong_ke = await self.get_by_bai_kiem_tra_va_lop_hoc(bai_kiem_tra_id, lop_hoc_id)
        
        # Lấy danh sách kết quả học sinh
        ket_qua_service = KetQuaService(self.db)
        ket_qua_hoc_sinh = await ket_qua_service.get_ket_qua_hoc_sinh_response(
            bai_kiem_tra_id, lop_hoc_id
        )
        
        if not thong_ke:
            # Trả về thống kê mặc định nếu chưa có
            return ThongKeResponse(
                tong_so_hoc_sinh=len(ket_qua_hoc_sinh),
                so_hoc_sinh_da_nop=sum(1 for kq in ket_qua_hoc_sinh if kq.trang_thai),
                diem_trung_binh=0.0,
                diem_cao_nhat=0.0,
                diem_thap_nhat=0.0,
                ket_qua=ket_qua_hoc_sinh
            )
        
        # Trả về thống kê đã có
        return ThongKeResponse(
            tong_so_hoc_sinh=len(ket_qua_hoc_sinh),
            so_hoc_sinh_da_nop=thong_ke.soLuongThamGia,
            diem_trung_binh=float(thong_ke.diemTrungBinh) if thong_ke.diemTrungBinh else 0.0,
            diem_cao_nhat=float(thong_ke.diemCaoNhat) if thong_ke.diemCaoNhat else 0.0,
            diem_thap_nhat=float(thong_ke.diemThapNhat) if thong_ke.diemThapNhat else 0.0,
            ket_qua=ket_qua_hoc_sinh
        )
    
    async def create(self, obj_in: ThongKeKiemTraCreate) -> ThongKeKiemTra:
        """
        Tạo thống kê kiểm tra mới
        """
        # Kiểm tra xem đã có thống kê chưa
        existing = await self.get_by_bai_kiem_tra_va_lop_hoc(
            obj_in.bai_kiem_tra_id, obj_in.lop_hoc_id
        )
        if existing:
            return existing
        
        # Tạo thống kê mới với dữ liệu mặc định
        db_obj = ThongKeKiemTra(
            maBaiKiemTra=obj_in.bai_kiem_tra_id,
            maLopHoc=obj_in.lop_hoc_id,
            soLuongThamGia=0,
            diemTrungBinh=Decimal('0.0'),
            diemCaoNhat=Decimal('0.0'),
            diemThapNhat=Decimal('0.0'),
            diemTrungVi=Decimal('0.0'),
            doLechChuan=Decimal('0.0'),
            thongKeCauHoiJSON={},
            phanLoaiDoKhoJSON={},
            phanBoDiemJSON={}
        )
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        # Cập nhật thống kê
        await self.update_thong_ke(db_obj.id)
        
        return db_obj
    
    async def update_thong_ke(self, id: int) -> Optional[ThongKeKiemTra]:
        """
        Cập nhật thống kê kiểm tra
        """
        thong_ke = await self.get_by_id(id)
        if not thong_ke:
            return None
        
        # Lấy danh sách kết quả
        stmt = select(KetQua).join(
            HocSinh, KetQua.maHocSinh == HocSinh.id
        ).where(
            KetQua.maBaiKiemTra == thong_ke.maBaiKiemTra,
            HocSinh.maLopHoc == thong_ke.maLopHoc
        )
        
        result = await self.db.execute(stmt)
        ket_quas = result.scalars().all()
        
        # Tính toán thống kê
        if not ket_quas:
            # Không có kết quả nào, giữ nguyên hoặc reset về 0
            thong_ke.soLuongThamGia = 0
            thong_ke.diemTrungBinh = Decimal('0.0')
            thong_ke.diemCaoNhat = Decimal('0.0')
            thong_ke.diemThapNhat = Decimal('0.0')
            thong_ke.diemTrungVi = Decimal('0.0')
            thong_ke.doLechChuan = Decimal('0.0')
        else:
            # Tính các giá trị thống kê
            diem_list = [float(kq.diem) for kq in ket_quas]
            diem_list.sort()
            
            thong_ke.soLuongThamGia = len(ket_quas)
            thong_ke.diemTrungBinh = Decimal(str(sum(diem_list) / len(diem_list)))
            thong_ke.diemCaoNhat = Decimal(str(max(diem_list)))
            thong_ke.diemThapNhat = Decimal(str(min(diem_list)))
            
            # Tính điểm trung vị
            n = len(diem_list)
            if n % 2 == 0:
                thong_ke.diemTrungVi = Decimal(str((diem_list[n//2-1] + diem_list[n//2]) / 2))
            else:
                thong_ke.diemTrungVi = Decimal(str(diem_list[n//2]))
            
            # Tính độ lệch chuẩn
            if len(diem_list) > 1:
                variance = sum((x - float(thong_ke.diemTrungBinh)) ** 2 for x in diem_list) / len(diem_list)
                thong_ke.doLechChuan = Decimal(str(variance ** 0.5))
            else:
                thong_ke.doLechChuan = Decimal('0.0')
            
            # Thống kê phân bố điểm
            phan_bo_diem = {}
            for diem in diem_list:
                diem_int = int(diem)
                phan_bo_diem[diem_int] = phan_bo_diem.get(diem_int, 0) + 1
            
            thong_ke.phanBoDiemJSON = phan_bo_diem
        
        self.db.add(thong_ke)
        await self.db.commit()
        await self.db.refresh(thong_ke)
        
        return thong_ke 