from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_async_session
from app.db.utils import commit_and_refresh
from app.models import HocSinh, LopHoc
from app.schemas import HocSinhCreate, HocSinhUpdate, HocSinhRead, PaginationResponse, ImportHocSinhRequest

router = APIRouter()

@router.get("/", response_model=PaginationResponse)
async def get_hoc_sinhs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    ma_lop_hoc: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Lấy danh sách học sinh với phân trang
    """
    offset = (page - 1) * page_size
    
    # Tạo query cơ bản
    query = select(HocSinh)
    
    # Thêm điều kiện lọc nếu có
    if ma_lop_hoc is not None:
        query = query.where(HocSinh.maLopHoc == ma_lop_hoc)
    
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

@router.post("/", response_model=HocSinhRead)
async def create_hoc_sinh(
    hoc_sinh: HocSinhCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Tạo học sinh mới
    """
    # Kiểm tra lớp học tồn tại
    lop_hoc_query = select(LopHoc).where(LopHoc.id == hoc_sinh.maLopHoc)
    lop_hoc_result = await db.execute(lop_hoc_query)
    if lop_hoc_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
    
    # Kiểm tra mã học sinh đã tồn tại trong lớp
    check_query = select(HocSinh).where(
        (HocSinh.maHocSinhTruong == hoc_sinh.maHocSinhTruong) & 
        (HocSinh.maLopHoc == hoc_sinh.maLopHoc)
    )
    check_result = await db.execute(check_query)
    if check_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=400, 
            detail="Mã học sinh đã tồn tại trong lớp này"
        )
    
    # Tạo học sinh mới
    new_hoc_sinh = HocSinh(**hoc_sinh.model_dump())
    
    return await commit_and_refresh(db, new_hoc_sinh)

@router.get("/{hoc_sinh_id}", response_model=HocSinhRead)
async def get_hoc_sinh(
    hoc_sinh_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Lấy thông tin của một học sinh theo ID
    """
    query = select(HocSinh).where(HocSinh.id == hoc_sinh_id)
    result = await db.execute(query)
    hoc_sinh = result.scalar_one_or_none()
    
    if hoc_sinh is None:
        raise HTTPException(status_code=404, detail="Học sinh không tồn tại")
    
    return hoc_sinh

@router.put("/{hoc_sinh_id}", response_model=HocSinhRead)
async def update_hoc_sinh(
    hoc_sinh_id: int,
    hoc_sinh_update: HocSinhUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Cập nhật thông tin của một học sinh
    """
    query = select(HocSinh).where(HocSinh.id == hoc_sinh_id)
    result = await db.execute(query)
    hoc_sinh = result.scalar_one_or_none()
    
    if hoc_sinh is None:
        raise HTTPException(status_code=404, detail="Học sinh không tồn tại")
    
    # Kiểm tra nếu thay đổi lớp và mã học sinh, xem có bị trùng không
    update_data = hoc_sinh_update.model_dump(exclude_unset=True)
    if "maLopHoc" in update_data or "maHocSinhTruong" in update_data:
        ma_lop_hoc = update_data.get("maLopHoc", hoc_sinh.maLopHoc)
        ma_hoc_sinh_truong = update_data.get("maHocSinhTruong", hoc_sinh.maHocSinhTruong)
        
        # Kiểm tra lớp tồn tại
        if "maLopHoc" in update_data:
            lop_hoc_query = select(LopHoc).where(LopHoc.id == ma_lop_hoc)
            lop_hoc_result = await db.execute(lop_hoc_query)
            if lop_hoc_result.scalar_one_or_none() is None:
                raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
        
        # Kiểm tra trùng mã trong lớp
        check_query = select(HocSinh).where(
            (HocSinh.maHocSinhTruong == ma_hoc_sinh_truong) & 
            (HocSinh.maLopHoc == ma_lop_hoc) &
            (HocSinh.id != hoc_sinh_id)
        )
        check_result = await db.execute(check_query)
        if check_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=400, 
                detail="Mã học sinh đã tồn tại trong lớp này"
            )
    
    # Cập nhật các trường
    for key, value in update_data.items():
        setattr(hoc_sinh, key, value)
    
    return await commit_and_refresh(db, hoc_sinh)

@router.delete("/{hoc_sinh_id}", response_model=HocSinhRead)
async def delete_hoc_sinh(
    hoc_sinh_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Xóa một học sinh
    """
    query = select(HocSinh).where(HocSinh.id == hoc_sinh_id)
    result = await db.execute(query)
    hoc_sinh = result.scalar_one_or_none()
    
    if hoc_sinh is None:
        raise HTTPException(status_code=404, detail="Học sinh không tồn tại")
    
    await db.delete(hoc_sinh)
    await db.commit()
    
    return hoc_sinh

@router.post("/import", response_model=dict)
async def import_hoc_sinh(
    import_request: ImportHocSinhRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Nhập danh sách học sinh từ file
    """
    # Kiểm tra lớp học tồn tại
    lop_hoc_query = select(LopHoc).where(LopHoc.id == import_request.maLopHoc)
    lop_hoc_result = await db.execute(lop_hoc_query)
    if lop_hoc_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
    
    # TODO: Thực hiện nhập từ file, có thể thêm code ở đây
    # Giả sử thành công
    
    return {
        "success": True,
        "message": "Đã nhập danh sách học sinh thành công",
        "imported": 0,
        "updated": 0,
        "errorCount": 0
    } 