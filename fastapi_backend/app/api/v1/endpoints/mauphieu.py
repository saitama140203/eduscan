from typing import Any, List

from fastapi import APIRouter, HTTPException, status, Path
from sqlalchemy import select

from app.api.deps import SessionDep, CurrentUser
from app.schemas.base import ResponseSchema
from app.schemas.mauphieu import (
    MauPhieuTraLoiCreate,
    MauPhieuTraLoiUpdate,
    MauPhieuTraLoiRead,
)
from app.services.mauphieu import MauPhieuTraLoiService


router = APIRouter()


@router.get("/", response_model=ResponseSchema[List[MauPhieuTraLoiRead]])
async def get_all_mau_phieu(
    db: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Lấy danh sách mẫu phiếu trả lời
    """
    service = MauPhieuTraLoiService(db)
    mau_phieu_list = await service.get_multi(
        skip=skip,
        limit=limit,
        maToChuc=current_user.toChucId
    )
    return ResponseSchema(
        success=True,
        message="Danh sách mẫu phiếu trả lời",
        data=mau_phieu_list
    )


@router.post("/", response_model=ResponseSchema[MauPhieuTraLoiRead])
async def create_mau_phieu(
    mau_phieu_in: MauPhieuTraLoiCreate,
    db: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Tạo mẫu phiếu trả lời mới
    """
    # Đảm bảo tổ chức và người tạo được set đúng
    if not mau_phieu_in.to_chuc_id:
        mau_phieu_in.to_chuc_id = current_user.toChucId
    if not mau_phieu_in.nguoi_tao_id:
        mau_phieu_in.nguoi_tao_id = current_user.id

    service = MauPhieuTraLoiService(db)
    mau_phieu = await service.create(obj_in=mau_phieu_in)
    return ResponseSchema(
        success=True,
        message="Đã tạo mẫu phiếu trả lời mới",
        data=mau_phieu
    )


@router.get("/{id}", response_model=ResponseSchema[MauPhieuTraLoiRead])
async def get_mau_phieu(
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Lấy thông tin mẫu phiếu trả lời theo ID
    """
    service = MauPhieuTraLoiService(db)
    mau_phieu = await service.get_by_id(id)
    
    if not mau_phieu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mẫu phiếu trả lời không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if mau_phieu.maToChuc != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập mẫu phiếu này",
        )
    
    return ResponseSchema(
        success=True,
        message="Thông tin mẫu phiếu trả lời",
        data=mau_phieu
    )


@router.put("/{id}", response_model=ResponseSchema[MauPhieuTraLoiRead])
async def update_mau_phieu(
    mau_phieu_in: MauPhieuTraLoiUpdate,
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Cập nhật thông tin mẫu phiếu trả lời
    """
    service = MauPhieuTraLoiService(db)
    mau_phieu = await service.get_by_id(id)
    
    if not mau_phieu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mẫu phiếu trả lời không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if mau_phieu.maToChuc != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền cập nhật mẫu phiếu này",
        )
    
    updated_mau_phieu = await service.update(db_obj=mau_phieu, obj_in=mau_phieu_in)
    return ResponseSchema(
        success=True,
        message="Đã cập nhật mẫu phiếu trả lời",
        data=updated_mau_phieu
    )


@router.delete("/{id}", response_model=ResponseSchema)
async def delete_mau_phieu(
    id: int = Path(..., gt=0),
    db: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Xóa mẫu phiếu trả lời
    """
    service = MauPhieuTraLoiService(db)
    mau_phieu = await service.get_by_id(id)
    
    if not mau_phieu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mẫu phiếu trả lời không tồn tại",
        )
    
    # Kiểm tra quyền truy cập
    if mau_phieu.maToChuc != current_user.toChucId and current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xóa mẫu phiếu này",
        )
    
    await service.delete_by_id(id)
    return ResponseSchema(
        success=True,
        message="Đã xóa mẫu phiếu trả lời"
    ) 