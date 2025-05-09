from typing import Any, List

from fastapi import APIRouter, HTTPException, status, Path

from app.api.deps import SessionDep, CurrentUser, CurrentAdminUser
from app.schemas.base import ResponseSchema
from app.schemas.caidat import CaiDatCreate, CaiDatUpdate, CaiDatRead
from app.services.caidat import CaiDatService


router = APIRouter()


@router.get("/", response_model=ResponseSchema[List[CaiDatRead]])
async def get_all_cai_dat(
    db: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Lấy danh sách cài đặt của tổ chức
    """
    service = CaiDatService(db)
    cai_dat_list = await service.get_multi(
        to_chuc_id=current_user.toChucId,
        skip=skip,
        limit=limit
    )
    
    return ResponseSchema(
        success=True,
        message="Danh sách cài đặt",
        data=cai_dat_list
    )


@router.post("/", response_model=ResponseSchema[CaiDatRead])
async def create_cai_dat(
    cai_dat_in: CaiDatCreate,
    db: SessionDep,
    current_user: CurrentAdminUser,
) -> Any:
    """
    Tạo cài đặt mới (yêu cầu quyền admin)
    """
    # Kiểm tra tổ chức ID
    if cai_dat_in.to_chuc_id != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền tạo cài đặt cho tổ chức khác",
        )
    
    service = CaiDatService(db)
    
    # Kiểm tra xem cài đặt đã tồn tại chưa
    existing = await service.get_by_name(to_chuc_id=cai_dat_in.to_chuc_id, ten_cai_dat=cai_dat_in.ten_cai_dat)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cài đặt '{cai_dat_in.ten_cai_dat}' đã tồn tại",
        )
    
    cai_dat = await service.create(obj_in=cai_dat_in)
    
    return ResponseSchema(
        success=True,
        message="Đã tạo cài đặt mới",
        data=cai_dat
    )


@router.get("/{id}", response_model=ResponseSchema[CaiDatRead])
async def get_cai_dat(
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Lấy thông tin cài đặt theo ID
    """
    service = CaiDatService(db)
    cai_dat = await service.get(id=id)
    
    if not cai_dat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cài đặt không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if cai_dat.to_chuc_id != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập cài đặt này",
        )
    
    return ResponseSchema(
        success=True,
        message="Thông tin cài đặt",
        data=cai_dat
    )


@router.put("/{id}", response_model=ResponseSchema[CaiDatRead])
async def update_cai_dat(
    cai_dat_in: CaiDatUpdate,
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Cập nhật thông tin cài đặt
    """
    service = CaiDatService(db)
    cai_dat = await service.get(id=id)
    
    if not cai_dat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cài đặt không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if cai_dat.to_chuc_id != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền cập nhật cài đặt này",
        )
    
    updated_cai_dat = await service.update(db_obj=cai_dat, obj_in=cai_dat_in)
    
    return ResponseSchema(
        success=True,
        message="Đã cập nhật cài đặt",
        data=updated_cai_dat
    )


@router.delete("/{id}", response_model=ResponseSchema)
async def delete_cai_dat(
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentAdminUser = None,
) -> Any:
    """
    Xóa cài đặt (yêu cầu quyền admin)
    """
    service = CaiDatService(db)
    cai_dat = await service.get(id=id)
    
    if not cai_dat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cài đặt không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if cai_dat.to_chuc_id != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xóa cài đặt này",
        )
    
    await service.delete(id=id)
    
    return ResponseSchema(
        success=True,
        message="Đã xóa cài đặt"
    )


@router.get("/theo-ten/{ten_cai_dat}", response_model=ResponseSchema[CaiDatRead])
async def get_cai_dat_by_name(
    ten_cai_dat: str,
    db: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Lấy thông tin cài đặt theo tên
    """
    service = CaiDatService(db)
    cai_dat = await service.get_by_name(to_chuc_id=current_user.toChucId, ten_cai_dat=ten_cai_dat)
    
    if not cai_dat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cài đặt '{ten_cai_dat}' không tồn tại",
        )
    
    return ResponseSchema(
        success=True,
        message="Thông tin cài đặt",
        data=cai_dat
    ) 