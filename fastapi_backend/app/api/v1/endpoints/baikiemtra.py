from typing import Any, List

from fastapi import APIRouter, HTTPException, status, Path
from pydantic import BaseModel

from app.api.deps import SessionDep, CurrentUser
from app.schemas.base import ResponseSchema
from app.schemas.baikiemtra import (
    BaiKiemTraCreate, BaiKiemTraUpdate, BaiKiemTraRead,
    DapAnCreate, DapAnUpdate, DapAnRead, TrangThaiBaiKiemTra,
    BaiKiemTraLopHocCreate, BaiKiemTraWithLopHoc
)
from app.services.baikiemtra import BaiKiemTraService, DapAnService


router = APIRouter()


@router.get("/", response_model=ResponseSchema[List[BaiKiemTraRead]])
async def get_all_bai_kiem_tra(
    db: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Lấy danh sách bài kiểm tra
    """
    service = BaiKiemTraService(db)
    bai_kiem_tra_list = await service.get_multi(
        skip=skip,
        limit=limit,
        maToChuc=current_user.toChucId
    )
    return ResponseSchema(
        success=True,
        message="Danh sách bài kiểm tra",
        data=bai_kiem_tra_list
    )


@router.post("/", response_model=ResponseSchema[BaiKiemTraRead])
async def create_bai_kiem_tra(
    bai_kiem_tra_in: BaiKiemTraCreate,
    db: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Tạo bài kiểm tra mới
    """
    service = BaiKiemTraService(db)
    
    # Gán thông tin người tạo
    if not bai_kiem_tra_in.nguoi_tao_id:
        bai_kiem_tra_in.nguoi_tao_id = current_user.id
        
    # Gán thông tin tổ chức
    if not bai_kiem_tra_in.to_chuc_id:
        bai_kiem_tra_in.to_chuc_id = current_user.toChucId
    
    bai_kiem_tra = await service.create(obj_in=bai_kiem_tra_in)
    return ResponseSchema(
        success=True,
        message="Đã tạo bài kiểm tra mới",
        data=bai_kiem_tra
    )


@router.get("/{id}", response_model=ResponseSchema[BaiKiemTraWithLopHoc])
async def get_bai_kiem_tra(
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Lấy thông tin bài kiểm tra theo ID
    """
    service = BaiKiemTraService(db)
    bai_kiem_tra = await service.get_with_lop_hoc(id=id)
    
    if not bai_kiem_tra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bài kiểm tra không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if bai_kiem_tra.to_chuc_id != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập bài kiểm tra này",
        )
    
    return ResponseSchema(
        success=True,
        message="Thông tin bài kiểm tra",
        data=bai_kiem_tra
    )


@router.put("/{id}", response_model=ResponseSchema[BaiKiemTraRead])
async def update_bai_kiem_tra(
    bai_kiem_tra_in: BaiKiemTraUpdate,
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Cập nhật thông tin bài kiểm tra
    """
    service = BaiKiemTraService(db)
    bai_kiem_tra = await service.get_by_id(id)
    
    if not bai_kiem_tra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bài kiểm tra không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if bai_kiem_tra.maToChuc != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền cập nhật bài kiểm tra này",
        )
    
    updated_bai_kiem_tra = await service.update(db_obj=bai_kiem_tra, obj_in=bai_kiem_tra_in)
    return ResponseSchema(
        success=True,
        message="Đã cập nhật bài kiểm tra",
        data=updated_bai_kiem_tra
    )


@router.delete("/{id}", response_model=ResponseSchema)
async def delete_bai_kiem_tra(
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Xóa bài kiểm tra
    """
    service = BaiKiemTraService(db)
    bai_kiem_tra = await service.get_by_id(id)
    
    if not bai_kiem_tra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bài kiểm tra không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if bai_kiem_tra.maToChuc != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xóa bài kiểm tra này",
        )
    
    await service.delete_by_id(id)
    return ResponseSchema(
        success=True,
        message="Đã xóa bài kiểm tra"
    )


# Endpoint cho đáp án
@router.post("/dapan", response_model=ResponseSchema[DapAnRead])
async def create_dap_an(
    dap_an_in: DapAnCreate,
    db: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Tạo đáp án mới cho bài kiểm tra
    """
    # Kiểm tra quyền đối với bài kiểm tra
    bai_kiem_tra_service = BaiKiemTraService(db)
    bai_kiem_tra = await bai_kiem_tra_service.get_by_id(dap_an_in.bai_kiem_tra_id)
    
    if not bai_kiem_tra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bài kiểm tra không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if bai_kiem_tra.maToChuc != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền thêm đáp án cho bài kiểm tra này",
        )
    
    dap_an_service = DapAnService(db)
    dap_an = await dap_an_service.create(obj_in=dap_an_in)
    
    return ResponseSchema(
        success=True,
        message="Đã tạo đáp án mới",
        data=dap_an
    )


@router.put("/dapan/{id}", response_model=ResponseSchema[DapAnRead])
async def update_dap_an(
    dap_an_in: DapAnUpdate,
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Cập nhật đáp án
    """
    dap_an_service = DapAnService(db)
    dap_an = await dap_an_service.get_by_id(id)
    
    if not dap_an:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Đáp án không tồn tại",
        )
    
    # Kiểm tra quyền đối với bài kiểm tra
    bai_kiem_tra_service = BaiKiemTraService(db)
    bai_kiem_tra = await bai_kiem_tra_service.get_by_id(dap_an.maBaiKiemTra)
    
    # Kiểm tra quyền truy cập
    if bai_kiem_tra.maToChuc != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền cập nhật đáp án cho bài kiểm tra này",
        )
    
    updated_dap_an = await dap_an_service.update(db_obj=dap_an, obj_in=dap_an_in)
    
    return ResponseSchema(
        success=True,
        message="Đã cập nhật đáp án",
        data=updated_dap_an
    )


@router.delete("/dapan/{id}", response_model=ResponseSchema)
async def delete_dap_an(
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Xóa đáp án
    """
    dap_an_service = DapAnService(db)
    dap_an = await dap_an_service.get_by_id(id)
    
    if not dap_an:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Đáp án không tồn tại",
        )
    
    # Kiểm tra quyền đối với bài kiểm tra
    bai_kiem_tra_service = BaiKiemTraService(db)
    bai_kiem_tra = await bai_kiem_tra_service.get_by_id(dap_an.maBaiKiemTra)
    
    # Kiểm tra quyền truy cập
    if bai_kiem_tra.maToChuc != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xóa đáp án của bài kiểm tra này",
        )
    
    await dap_an_service.delete_by_id(id)
    
    return ResponseSchema(
        success=True,
        message="Đã xóa đáp án"
    )


@router.post("/lophoc", response_model=ResponseSchema)
async def assign_bai_kiem_tra_to_lop_hoc(
    assignment: BaiKiemTraLopHocCreate,
    db: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Gán bài kiểm tra cho lớp học
    """
    # Kiểm tra quyền đối với bài kiểm tra
    bai_kiem_tra_service = BaiKiemTraService(db)
    bai_kiem_tra = await bai_kiem_tra_service.get_by_id(assignment.bai_kiem_tra_id)
    
    if not bai_kiem_tra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bài kiểm tra không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if bai_kiem_tra.maToChuc != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền gán bài kiểm tra này",
        )
    
    await bai_kiem_tra_service.assign_to_lop_hoc(
        bai_kiem_tra_id=assignment.bai_kiem_tra_id,
        lop_hoc_id=assignment.lop_hoc_id
    )
    
    return ResponseSchema(
        success=True,
        message=f"Đã gán bài kiểm tra cho lớp học ID: {assignment.lop_hoc_id}"
    )


@router.delete("/lophoc/{bai_kiem_tra_id}/{lop_hoc_id}", response_model=ResponseSchema)
async def unassign_bai_kiem_tra_from_lop_hoc(
    bai_kiem_tra_id: int = Path(..., gt=0),
    lop_hoc_id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Hủy gán bài kiểm tra khỏi lớp học
    """
    # Kiểm tra quyền đối với bài kiểm tra
    bai_kiem_tra_service = BaiKiemTraService(db)
    bai_kiem_tra = await bai_kiem_tra_service.get_by_id(bai_kiem_tra_id)
    
    if not bai_kiem_tra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bài kiểm tra không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if bai_kiem_tra.maToChuc != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền hủy gán bài kiểm tra này",
        )
    
    result = await bai_kiem_tra_service.unassign_from_lop_hoc(
        bai_kiem_tra_id=bai_kiem_tra_id,
        lop_hoc_id=lop_hoc_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy liên kết giữa bài kiểm tra và lớp học",
        )
    
    return ResponseSchema(
        success=True,
        message=f"Đã hủy gán bài kiểm tra khỏi lớp học ID: {lop_hoc_id}"
    ) 