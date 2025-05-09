from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from datetime import datetime

from app.db import get_async_session
from app.db.utils import commit_and_refresh
from app.models import NguoiDung, ToChuc
from app.schemas import (
    NguoiDungCreate, 
    NguoiDungUpdate, 
    NguoiDungRead, 
    NguoiDungProfileUpdate,
    ChangePasswordRequest, 
    ResponseSchema,
    UploadAvatarResponse
)
from app.api.deps import get_current_active_user, CurrentUser
from app.core.security import get_password_hash, verify_password
from app.services.file import FileService

router = APIRouter()


@router.get("/", response_model=ResponseSchema)
async def get_nguoi_dungs(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    to_chuc_id: Optional[int] = None,
    vai_tro: Optional[str] = None,
    trang_thai: Optional[str] = None
):
    """
    Lấy danh sách người dùng với phân trang và tìm kiếm
    """
    # Kiểm tra quyền truy cập
    if current_user.vaiTro not in ["admin", "manager"]:
        if to_chuc_id and to_chuc_id != current_user.toChucId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền xem người dùng của tổ chức khác"
            )
        # Mặc định chỉ xem người dùng cùng tổ chức
        to_chuc_id = current_user.toChucId
    
    # Tạo query cơ bản
    query = select(NguoiDung)
    
    # Thêm các điều kiện lọc
    if to_chuc_id:
        query = query.filter(NguoiDung.toChucId == to_chuc_id)
    
    if vai_tro:
        query = query.filter(NguoiDung.vaiTro == vai_tro)
    
    if trang_thai:
        query = query.filter(NguoiDung.trangThai == trang_thai)
    
    if search:
        query = query.filter(
            or_(
                NguoiDung.hoTen.ilike(f"%{search}%"),
                NguoiDung.email.ilike(f"%{search}%"),
                # NguoiDung.tenDangNhap.ilike(f"%{search}%")
            )
        )
    
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
        message="Danh sách người dùng",
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
async def create_nguoi_dung(
    nguoi_dung: NguoiDungCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Tạo người dùng mới
    """
    # Kiểm tra quyền truy cập
    if current_user.vaiTro not in ["admin", "manager"]:
        if nguoi_dung.toChucId != current_user.toChucId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền tạo người dùng cho tổ chức khác"
            )
    
    # Kiểm tra tổ chức tồn tại
    if nguoi_dung.toChucId:
        to_chuc_query = select(ToChuc).where(ToChuc.id == nguoi_dung.toChucId)
        to_chuc_result = await db.execute(to_chuc_query)
        if to_chuc_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tổ chức không tồn tại"
            )
    
    # Kiểm tra email đã tồn tại chưa
    email_query = select(NguoiDung).where(NguoiDung.email == nguoi_dung.email)
    email_result = await db.execute(email_query)
    if email_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    

    
    # Tạo dữ liệu người dùng mới
    nguoi_dung_data = nguoi_dung.model_dump(exclude={"xacNhanMatKhau"})
    
    # Hash mật khẩu
    matKhau = nguoi_dung_data.pop("matKhau")
    matKhau_hash = get_password_hash(matKhau)
    
    # Tạo đối tượng NguoiDung
    new_nguoi_dung = NguoiDung(**nguoi_dung_data, matKhau=matKhau_hash)
    
    # Lưu vào database
    created_nguoi_dung = await commit_and_refresh(db, new_nguoi_dung)
    
    return ResponseSchema(
        success=True,
        message="Tạo người dùng thành công",
        data=created_nguoi_dung
    )


@router.get("/me", response_model=ResponseSchema)
async def get_current_user_info(
    current_user: CurrentUser
):
    """
    Lấy thông tin người dùng hiện tại
    """
    return ResponseSchema(
        success=True,
        message="Thông tin người dùng hiện tại",
        data=current_user
    )


@router.get("/{nguoi_dung_id}", response_model=ResponseSchema)
async def get_nguoi_dung(
    nguoi_dung_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Lấy thông tin của một người dùng theo ID
    """
    # Lấy người dùng
    query = select(NguoiDung).where(NguoiDung.id == nguoi_dung_id)
    result = await db.execute(query)
    nguoi_dung = result.scalar_one_or_none()
    
    if nguoi_dung is None:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    # Kiểm tra quyền
    if (current_user.id != nguoi_dung_id and 
        current_user.vaiTro not in ["admin", "manager"] and
        current_user.toChucId != nguoi_dung.toChucId):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xem thông tin người dùng này"
        )
    
    return ResponseSchema(
        success=True,
        message="Thông tin người dùng",
        data=nguoi_dung
    )


@router.put("/me", response_model=ResponseSchema)
async def update_own_profile(
    profile_update: NguoiDungProfileUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Cập nhật thông tin cá nhân của người dùng hiện tại
    """
    # Lấy người dùng hiện tại
    query = select(NguoiDung).where(NguoiDung.id == current_user.id)
    result = await db.execute(query)
    nguoi_dung = result.scalar_one_or_none()
    
    if nguoi_dung is None:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    # Cập nhật các trường thay đổi
    update_data = profile_update.model_dump(exclude_unset=True)
    
    # Kiểm tra email trùng lặp nếu thay đổi
    if "email" in update_data and update_data["email"] != nguoi_dung.email:
        email_query = select(NguoiDung).where(
            NguoiDung.email == update_data["email"],
            NguoiDung.id != current_user.id
        )
        email_result = await db.execute(email_query)
        if email_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng bởi người dùng khác"
            )
    
    # Cập nhật các trường
    for key, value in update_data.items():
        setattr(nguoi_dung, key, value)
    
    # Lưu vào database
    updated_nguoi_dung = await commit_and_refresh(db, nguoi_dung)
    
    return ResponseSchema(
        success=True,
        message="Cập nhật thông tin cá nhân thành công",
        data=updated_nguoi_dung
    )


@router.post("/me/change-password", response_model=ResponseSchema)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Đổi mật khẩu của người dùng hiện tại
    """
    # Lấy người dùng hiện tại
    query = select(NguoiDung).where(NguoiDung.id == current_user.id)
    result = await db.execute(query)
    nguoi_dung = result.scalar_one_or_none()
    
    if nguoi_dung is None:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    # Kiểm tra mật khẩu hiện tại
    if not verify_password(password_data.matKhauHienTai, nguoi_dung.matKhau):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không đúng"
        )
    
    # Cập nhật mật khẩu mới
    nguoi_dung.matKhau = get_password_hash(password_data.matKhauMoi)
    
    # Lưu vào database
    await commit_and_refresh(db, nguoi_dung)
    
    return ResponseSchema(
        success=True,
        message="Đổi mật khẩu thành công"
    )


@router.post("/me/avatar", response_model=ResponseSchema)
async def upload_own_avatar(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session),
    file: UploadFile = File(...),
    file_service: FileService = Depends(FileService)
):
    """
    Upload ảnh đại diện cho người dùng hiện tại
    """
    # Lấy người dùng hiện tại
    query = select(NguoiDung).where(NguoiDung.id == current_user.id)
    result = await db.execute(query)
    nguoi_dung = result.scalar_one_or_none()
    
    if nguoi_dung is None:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    # Xử lý upload ảnh đại diện
    file_url = await file_service.upload_avatar(
        file=file,
        nguoi_dung_id=current_user.id
    )
    
    # Cập nhật url ảnh đại diện cho người dùng
    old_avatar = nguoi_dung.urlAnhDaiDien
    nguoi_dung.urlAnhDaiDien = file_url
    updated_nguoi_dung = await commit_and_refresh(db, nguoi_dung)
    
    # Xóa ảnh đại diện cũ nếu có
    if old_avatar:
        await file_service.delete_file(old_avatar)
    
    return ResponseSchema(
        success=True,
        message="Upload ảnh đại diện thành công",
        data={"urlAnhDaiDien": file_url}
    )


@router.put("/{nguoi_dung_id}", response_model=ResponseSchema)
async def update_nguoi_dung(
    nguoi_dung_id: int,
    nguoi_dung_update: NguoiDungUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Cập nhật thông tin của một người dùng
    """
    # Kiểm tra quyền
    if (current_user.id != nguoi_dung_id and 
        current_user.vaiTro not in ["admin", "manager"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền cập nhật thông tin người dùng này"
        )
    
    # Lấy người dùng hiện tại
    query = select(NguoiDung).where(NguoiDung.id == nguoi_dung_id)
    result = await db.execute(query)
    nguoi_dung = result.scalar_one_or_none()
    
    if nguoi_dung is None:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    # Kiểm tra thêm quyền nếu là Manager
    if current_user.vaiTro == "manager":
        if nguoi_dung.toChucId != current_user.toChucId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền cập nhật người dùng của tổ chức khác"
            )
        
        # Manager không thể thay đổi vai trò của admin
        if nguoi_dung.vaiTro == "admin" and "vaiTro" in nguoi_dung_update.model_dump(exclude_unset=True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không thể thay đổi vai trò của Admin"
            )
    
    # Cập nhật các trường thay đổi
    update_data = nguoi_dung_update.model_dump(exclude_unset=True)
    
    # Kiểm tra email trùng lặp nếu thay đổi
    if "email" in update_data and update_data["email"] != nguoi_dung.email:
        email_query = select(NguoiDung).where(
            NguoiDung.email == update_data["email"],
            NguoiDung.id != nguoi_dung_id
        )
        email_result = await db.execute(email_query)
        if email_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng bởi người dùng khác"
            )
    

    
    # Xử lý riêng cho mật khẩu nếu có thay đổi
    if "matKhau" in update_data:
        matKhau = update_data.pop("matKhau")
        nguoi_dung.matKhau = get_password_hash(matKhau)
    
    # Cập nhật các trường còn lại
    for key, value in update_data.items():
        setattr(nguoi_dung, key, value)
    
    # Lưu vào database
    updated_nguoi_dung = await commit_and_refresh(db, nguoi_dung)
    
    return ResponseSchema(
        success=True,
        message="Cập nhật người dùng thành công",
        data=updated_nguoi_dung
    )


@router.delete("/{nguoi_dung_id}", response_model=ResponseSchema)
async def delete_nguoi_dung(
    nguoi_dung_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Xóa một người dùng
    """
    # Kiểm tra quyền admin hoặc quản lý
    if current_user.vaiTro not in [VaiTroNguoiDung.ADMIN, VaiTroNguoiDung.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xóa người dùng"
        )
    
    # Ngăn chặn xóa chính mình
    if nguoi_dung_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa tài khoản của chính mình"
        )
    
    # Lấy người dùng cần xóa
    query = select(NguoiDung).where(NguoiDung.id == nguoi_dung_id)
    result = await db.execute(query)
    nguoi_dung = result.scalar_one_or_none()
    
    if nguoi_dung is None:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    # Kiểm tra quyền nếu là Manager
    if current_user.vaiTro == VaiTroNguoiDung.MANAGER:
        # Manager chỉ có thể xóa người dùng trong cùng tổ chức
        if nguoi_dung.toChucId != current_user.toChucId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền xóa người dùng của tổ chức khác"
            )
        
        # Manager không thể xóa Admin
        if nguoi_dung.vaiTro == VaiTroNguoiDung.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không thể xóa tài khoản Admin"
            )
    
    # Xóa ảnh đại diện nếu có
    if nguoi_dung.urlAnhDaiDien:
        file_service = FileService()
        await file_service.delete_file(nguoi_dung.urlAnhDaiDien)
    
    # Xóa người dùng
    await db.delete(nguoi_dung)
    await db.commit()
    
    return ResponseSchema(
        success=True,
        message="Xóa người dùng thành công",
        data={"id": nguoi_dung_id}
    )


@router.put("/{nguoi_dung_id}/last-login", response_model=ResponseSchema)
async def update_last_login(
    nguoi_dung_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Cập nhật thời gian đăng nhập cuối cùng
    """
    # Chỉ có thể cập nhật thời gian đăng nhập của chính mình
    if nguoi_dung_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ có thể cập nhật thời gian đăng nhập của chính mình"
        )
    
    # Lấy người dùng hiện tại
    query = select(NguoiDung).where(NguoiDung.id == nguoi_dung_id)
    result = await db.execute(query)
    nguoi_dung = result.scalar_one_or_none()
    
    if nguoi_dung is None:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    # Cập nhật thời gian đăng nhập cuối
    nguoi_dung.thoiGianDangNhapCuoi = datetime.utcnow()
    
    # Lưu vào database
    await commit_and_refresh(db, nguoi_dung)
    
    return ResponseSchema(
        success=True,
        message="Cập nhật thời gian đăng nhập thành công"
    ) 