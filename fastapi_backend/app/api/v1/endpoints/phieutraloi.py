from typing import Any, List

from fastapi import APIRouter, HTTPException, status, Path, Query
from sqlalchemy import select

from app.api.deps import SessionDep, CurrentUser
from app.schemas.base import ResponseSchema
from app.schemas.phieutraloi import (
    PhieuTraLoiCreate, PhieuTraLoiUpdate, PhieuTraLoiRead,
    KetQuaCreate, KetQuaUpdate, KetQuaRead,
    ThongKeResponse, KetQuaHocSinhResponse
)
from app.services.phieutraloi import PhieuTraLoiService, KetQuaService
from app.services.baikiemtra import BaiKiemTraService


router = APIRouter()


@router.post("/", response_model=ResponseSchema[PhieuTraLoiRead])
async def create_phieu_tra_loi(
    phieu_tra_loi_in: PhieuTraLoiCreate,
    db: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Tạo phiếu trả lời mới
    """
    # Kiểm tra quyền đối với bài kiểm tra
    bai_kiem_tra_service = BaiKiemTraService(db)
    bai_kiem_tra = await bai_kiem_tra_service.get(id=phieu_tra_loi_in.bai_kiem_tra_id)
    
    if not bai_kiem_tra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bài kiểm tra không tồn tại",
        )
    
    service = PhieuTraLoiService(db)
    phieu_tra_loi = await service.create(obj_in=phieu_tra_loi_in)
    
    return ResponseSchema(
        success=True,
        message="Đã tạo phiếu trả lời mới",
        data=phieu_tra_loi
    )


@router.get("/{id}", response_model=ResponseSchema[PhieuTraLoiRead])
async def get_phieu_tra_loi(
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Lấy thông tin phiếu trả lời theo ID
    """
    service = PhieuTraLoiService(db)
    phieu_tra_loi = await service.get(id=id)
    
    if not phieu_tra_loi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phiếu trả lời không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    # TODO: Bổ sung kiểm tra quyền truy cập, ví dụ học sinh chỉ được xem phiếu của mình
    
    return ResponseSchema(
        success=True,
        message="Thông tin phiếu trả lời",
        data=phieu_tra_loi
    )


@router.put("/{id}", response_model=ResponseSchema[PhieuTraLoiRead])
async def update_phieu_tra_loi(
    phieu_tra_loi_in: PhieuTraLoiUpdate,
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Cập nhật thông tin phiếu trả lời
    """
    service = PhieuTraLoiService(db)
    phieu_tra_loi = await service.get(id=id)
    
    if not phieu_tra_loi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phiếu trả lời không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    # TODO: Bổ sung kiểm tra quyền truy cập
    
    updated_phieu_tra_loi = await service.update(db_obj=phieu_tra_loi, obj_in=phieu_tra_loi_in)
    
    return ResponseSchema(
        success=True,
        message="Đã cập nhật phiếu trả lời",
        data=updated_phieu_tra_loi
    )


@router.post("/nop/{id}", response_model=ResponseSchema[PhieuTraLoiRead])
async def submit_phieu_tra_loi(
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Nộp phiếu trả lời
    """
    service = PhieuTraLoiService(db)
    phieu_tra_loi = await service.get(id=id)
    
    if not phieu_tra_loi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phiếu trả lời không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    # TODO: Bổ sung kiểm tra quyền truy cập
    
    # Cập nhật trạng thái đã nộp
    update_data = PhieuTraLoiUpdate(trang_thai=True)
    updated_phieu_tra_loi = await service.update(db_obj=phieu_tra_loi, obj_in=update_data)
    
    # Tính điểm cho phiếu đã nộp
    await service.calculate_score(id=id)
    
    return ResponseSchema(
        success=True,
        message="Đã nộp phiếu trả lời thành công",
        data=updated_phieu_tra_loi
    )


# Endpoints cho kết quả
@router.post("/ketqua", response_model=ResponseSchema[KetQuaRead])
async def create_ket_qua(
    ket_qua_in: KetQuaCreate,
    db: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Thêm kết quả cho phiếu trả lời
    """
    # Lấy thông tin phiếu
    phieu_service = PhieuTraLoiService(db)
    phieu = await phieu_service.get(id=ket_qua_in.phieu_tra_loi_id)
    
    if not phieu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phiếu trả lời không tồn tại",
        )
    
    # Kiểm tra xem phiếu đã nộp chưa
    if phieu.trang_thai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phiếu trả lời đã được nộp, không thể thêm kết quả",
        )
    
    # Kiểm tra quyền truy cập
    # TODO: Bổ sung kiểm tra quyền truy cập
    
    ket_qua_service = KetQuaService(db)
    ket_qua = await ket_qua_service.create(obj_in=ket_qua_in)
    
    return ResponseSchema(
        success=True,
        message="Đã thêm kết quả mới",
        data=ket_qua
    )


@router.put("/ketqua/{id}", response_model=ResponseSchema[KetQuaRead])
async def update_ket_qua(
    ket_qua_in: KetQuaUpdate,
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Cập nhật kết quả
    """
    ket_qua_service = KetQuaService(db)
    ket_qua = await ket_qua_service.get(id=id)
    
    if not ket_qua:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kết quả không tồn tại",
        )
    
    # Lấy thông tin phiếu
    phieu_service = PhieuTraLoiService(db)
    phieu = await phieu_service.get(id=ket_qua.phieu_tra_loi_id)
    
    # Kiểm tra xem phiếu đã nộp chưa
    if phieu.trang_thai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phiếu trả lời đã được nộp, không thể cập nhật kết quả",
        )
    
    # Kiểm tra quyền truy cập
    # TODO: Bổ sung kiểm tra quyền truy cập
    
    updated_ket_qua = await ket_qua_service.update(db_obj=ket_qua, obj_in=ket_qua_in)
    
    return ResponseSchema(
        success=True,
        message="Đã cập nhật kết quả",
        data=updated_ket_qua
    )


# Endpoint cho thống kê
@router.get("/thongke/baikiemtra/{bai_kiem_tra_id}/lophoc/{lop_hoc_id}", response_model=ResponseSchema[ThongKeResponse])
async def get_thong_ke_bai_kiem_tra(
    bai_kiem_tra_id: int = Path(..., gt=0),
    lop_hoc_id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Lấy thống kê kết quả bài kiểm tra theo lớp học
    """
    service = PhieuTraLoiService(db)
    thong_ke = await service.get_thong_ke_bai_kiem_tra(
        bai_kiem_tra_id=bai_kiem_tra_id,
        lop_hoc_id=lop_hoc_id
    )
    
    if not thong_ke:
        # Trả về dữ liệu rỗng nếu chưa có kết quả
        return ResponseSchema(
            success=True,
            message="Chưa có kết quả thống kê",
            data={
                "tong_so_hoc_sinh": 0,
                "so_hoc_sinh_da_nop": 0,
                "diem_trung_binh": 0,
                "diem_cao_nhat": 0,
                "diem_thap_nhat": 0,
                "ket_qua": []
            }
        )
    
    return ResponseSchema(
        success=True,
        message="Thống kê kết quả bài kiểm tra",
        data=thong_ke
    ) 