from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.db import get_async_session
from app.db.utils import commit_and_refresh
from app.models import ToChuc, NguoiDung, LopHoc
from app.schemas import ToChucCreate, ToChucUpdate, ToChucRead, ToChucDetail, ResponseSchema
from app.api.deps import get_current_active_user, CurrentUser
from app.services.file import FileService

router = APIRouter()

@router.get("/", response_model=ResponseSchema)
async def get_to_chucs(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    ten_to_chuc: Optional[str] = None,
    loai_to_chuc: Optional[str] = None,
    loai_hinh: Optional[str] = None
):
    """
    Lấy danh sách tổ chức với phân trang và tìm kiếm
    """
    # Tạo query cơ bản
    query = select(ToChuc)
    
    # Thêm các điều kiện lọc
    if ten_to_chuc:
        query = query.filter(ToChuc.tenToChuc.ilike(f"%{ten_to_chuc}%"))
    if loai_to_chuc:
        query = query.filter(ToChuc.loaiToChuc == loai_to_chuc)
    if loai_hinh:
        query = query.filter(ToChuc.loaiHinh == loai_hinh)
    
    # Đếm tổng số bản ghi phù hợp với điều kiện lọc
    count_query = select(func.count()).select_from(query.subquery())
    total_count = await db.scalar(count_query)
    
    # Thêm phân trang
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # Thực thi query
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Tính tổng số trang
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
    
    return ResponseSchema(
        success=True,
        message="Danh sách tổ chức",
        data={
            "items": items,
            "pagination": {
                "totalItems": total_count,
                "page": page,
                "pageSize": page_size,
                "totalPages": total_pages
            }
        }
    )

@router.post("/", response_model=ResponseSchema)
async def create_to_chuc(
    to_chuc: ToChucCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Tạo tổ chức mới
    """
    # Kiểm tra quyền admin
    if current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền thực hiện hành động này"
        )
    
    # Tạo đối tượng tổ chức mới
    new_to_chuc = ToChuc(**to_chuc.model_dump())
    
    # Lưu vào database
    created_to_chuc = await commit_and_refresh(db, new_to_chuc)
    
    return ResponseSchema(
        success=True,
        message="Tạo tổ chức thành công",
        data=created_to_chuc
    )

@router.get("/detail/{to_chuc_id}", response_model=ResponseSchema)
async def get_to_chuc_detail(
    to_chuc_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Lấy thông tin chi tiết của một tổ chức theo ID kèm theo số lượng người dùng và lớp học
    """
    # Lấy tổ chức
    query = select(ToChuc).where(ToChuc.id == to_chuc_id)
    result = await db.execute(query)
    to_chuc = result.scalar_one_or_none()
    
    if to_chuc is None:
        raise HTTPException(status_code=404, detail="Tổ chức không tồn tại")
    
    # Đếm số người dùng thuộc tổ chức
    nguoi_dung_count = await db.scalar(
        select(func.count()).select_from(
            select(NguoiDung).where(NguoiDung.toChucId == to_chuc_id).subquery()
        )
    )
    
    # Đếm số lớp học thuộc tổ chức
    lop_hoc_count = await db.scalar(
        select(func.count()).select_from(
            select(LopHoc).where(LopHoc.toChucId == to_chuc_id).subquery()
        )
    )
    
    # Tạo đối tượng kết quả
    to_chuc_detail = ToChucDetail(
        **to_chuc.__dict__, 
        soNguoiDung=nguoi_dung_count or 0,
        soLopHoc=lop_hoc_count or 0
    )
    
    return ResponseSchema(
        success=True,
        message="Thông tin chi tiết tổ chức",
        data=to_chuc_detail
    )

@router.get("/{to_chuc_id}", response_model=ResponseSchema)
async def get_to_chuc(
    to_chuc_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Lấy thông tin của một tổ chức theo ID
    """
    query = select(ToChuc).where(ToChuc.id == to_chuc_id)
    result = await db.execute(query)
    to_chuc = result.scalar_one_or_none()
    
    if to_chuc is None:
        raise HTTPException(status_code=404, detail="Tổ chức không tồn tại")
    
    return ResponseSchema(
        success=True,
        message="Thông tin tổ chức",
        data=to_chuc
    )

@router.put("/{to_chuc_id}", response_model=ResponseSchema)
async def update_to_chuc(
    to_chuc_id: int,
    to_chuc_update: ToChucUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Cập nhật thông tin của một tổ chức
    """
    # Kiểm tra quyền
    if current_user.vaiTro != "admin" and current_user.toChucId != to_chuc_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền thực hiện hành động này"
        )
    
    # Lấy tổ chức hiện tại
    query = select(ToChuc).where(ToChuc.id == to_chuc_id)
    result = await db.execute(query)
    to_chuc = result.scalar_one_or_none()
    
    if to_chuc is None:
        raise HTTPException(status_code=404, detail="Tổ chức không tồn tại")
    
    # Cập nhật các trường thay đổi
    update_data = to_chuc_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(to_chuc, key, value)
    
    # Lưu vào database
    updated_to_chuc = await commit_and_refresh(db, to_chuc)
    
    return ResponseSchema(
        success=True,
        message="Cập nhật tổ chức thành công",
        data=updated_to_chuc
    )

@router.post("/{to_chuc_id}/logo", response_model=ResponseSchema)
async def upload_to_chuc_logo(
    to_chuc_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session),
    file: UploadFile = File(...)
):
    """
    Upload logo cho tổ chức
    """
    # Kiểm tra quyền
    if current_user.vaiTro != "admin" and current_user.toChucId != to_chuc_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền thực hiện hành động này"
        )
    
    # Lấy tổ chức hiện tại
    query = select(ToChuc).where(ToChuc.id == to_chuc_id)
    result = await db.execute(query)
    to_chuc = result.scalar_one_or_none()
    
    if to_chuc is None:
        raise HTTPException(status_code=404, detail="Tổ chức không tồn tại")
    
    # Xử lý upload file
    file_service = FileService()
    file_url = await file_service.upload_logo(
        file=file,
        to_chuc_id=to_chuc_id,
        nguoi_dung_id=current_user.id
    )
    
    # Cập nhật url logo cho tổ chức
    to_chuc.urlLogo = file_url
    updated_to_chuc = await commit_and_refresh(db, to_chuc)
    
    return ResponseSchema(
        success=True,
        message="Upload logo thành công",
        data={"urlLogo": file_url}
    )

@router.delete("/{to_chuc_id}", response_model=ResponseSchema)
async def delete_to_chuc(
    to_chuc_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Xóa một tổ chức
    """
    # Kiểm tra quyền admin
    if current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền thực hiện hành động này"
        )
    
    # Lấy tổ chức
    query = select(ToChuc).where(ToChuc.id == to_chuc_id)
    result = await db.execute(query)
    to_chuc = result.scalar_one_or_none()
    
    if to_chuc is None:
        raise HTTPException(status_code=404, detail="Tổ chức không tồn tại")
    
    # Xóa tổ chức
    await db.delete(to_chuc)
    await db.commit()
    
    return ResponseSchema(
        success=True,
        message="Xóa tổ chức thành công",
        data=to_chuc
    )