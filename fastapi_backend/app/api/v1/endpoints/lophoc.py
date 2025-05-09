from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_async_session
from app.db.utils import commit_and_refresh
from app.models import LopHoc, ToChuc, NguoiDung
from app.schemas import LopHocCreate, LopHocUpdate, LopHocRead, PaginationResponse

router = APIRouter()

@router.get("/", response_model=PaginationResponse)
async def get_lop_hocs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    ma_to_chuc: Optional[int] = None,
    ma_giao_vien: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Lấy danh sách lớp học với phân trang
    """
    offset = (page - 1) * page_size
    
    # Tạo query cơ bản
    query = select(LopHoc)
    
    # Thêm điều kiện lọc nếu có
    if ma_to_chuc is not None:
        query = query.where(LopHoc.maToChuc == ma_to_chuc)
    
    if ma_giao_vien is not None:
        query = query.where(LopHoc.maGiaoVienChuNhiem == ma_giao_vien)
    
    # Query tổng số 
    total_result = await db.execute(query)
    total_items = len(total_result.scalars().all())
    
    # Query với phân trang
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Tính tổng số trang
    total_pages = (total_items + page_size - 1) // page_size
    
    return {
        "items": items,
        "totalItems": total_items,
        "page": page,
        "pageSize": page_size,
        "totalPages": total_pages
    }

@router.post("/", response_model=LopHocRead)
async def create_lop_hoc(
    lop_hoc: LopHocCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Tạo lớp học mới
    """
    # Kiểm tra tổ chức tồn tại
    to_chuc_query = select(ToChuc).where(ToChuc.id == lop_hoc.maToChuc)
    to_chuc_result = await db.execute(to_chuc_query)
    if to_chuc_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Tổ chức không tồn tại")
    
    # Kiểm tra giáo viên chủ nhiệm tồn tại nếu có
    if lop_hoc.maGiaoVienChuNhiem is not None:
        gv_query = select(NguoiDung).where(NguoiDung.id == lop_hoc.maGiaoVienChuNhiem)
        gv_result = await db.execute(gv_query)
        if gv_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Giáo viên chủ nhiệm không tồn tại")
    
    # Tạo lớp học mới
    new_lop_hoc = LopHoc(**lop_hoc.model_dump())
    
    return await commit_and_refresh(db, new_lop_hoc)

@router.get("/{lop_hoc_id}", response_model=LopHocRead)
async def get_lop_hoc(
    lop_hoc_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Lấy thông tin của một lớp học theo ID
    """
    query = select(LopHoc).where(LopHoc.id == lop_hoc_id)
    result = await db.execute(query)
    lop_hoc = result.scalar_one_or_none()
    
    if lop_hoc is None:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
    
    return lop_hoc

@router.put("/{lop_hoc_id}", response_model=LopHocRead)
async def update_lop_hoc(
    lop_hoc_id: int,
    lop_hoc_update: LopHocUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Cập nhật thông tin của một lớp học
    """
    query = select(LopHoc).where(LopHoc.id == lop_hoc_id)
    result = await db.execute(query)
    lop_hoc = result.scalar_one_or_none()
    
    if lop_hoc is None:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
    
    # Kiểm tra giáo viên chủ nhiệm tồn tại nếu được cập nhật
    update_data = lop_hoc_update.model_dump(exclude_unset=True)
    if "maGiaoVienChuNhiem" in update_data and update_data["maGiaoVienChuNhiem"] is not None:
        gv_query = select(NguoiDung).where(NguoiDung.id == update_data["maGiaoVienChuNhiem"])
        gv_result = await db.execute(gv_query)
        if gv_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Giáo viên chủ nhiệm không tồn tại")
    
    # Cập nhật các trường
    for key, value in update_data.items():
        setattr(lop_hoc, key, value)
    
    return await commit_and_refresh(db, lop_hoc)

@router.delete("/{lop_hoc_id}", response_model=LopHocRead)
async def delete_lop_hoc(
    lop_hoc_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Xóa một lớp học
    """
    query = select(LopHoc).where(LopHoc.id == lop_hoc_id)
    result = await db.execute(query)
    lop_hoc = result.scalar_one_or_none()
    
    if lop_hoc is None:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
    
    await db.delete(lop_hoc)
    await db.commit()
    
    return lop_hoc 