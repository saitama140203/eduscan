from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep, CurrentUser
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_reset_password_token,
    verify_reset_password_token,
)
from app.models.nguoidung import NguoiDung
from app.schemas.base import ResponseSchema
from app.schemas.token import (
    Token,
    LoginRequest,
    LoginResponse,
    PasswordResetRequest,
    NewPasswordRequest,
)
from app.services.nguoidung import NguoiDungService


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: LoginRequest,
    db: SessionDep,
) -> Any:
    """
    Xác thực và đăng nhập người dùng với email và mật khẩu
    """
    nguoi_dung_service = NguoiDungService(db)
    user = await nguoi_dung_service.authenticate(
        email=form_data.email, password=form_data.password
    )
     
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.trangThai:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động",
        )
    
    # Tạo scopes dựa trên vai trò
    scopes = ["user"]
    if user.vaiTro == "admin":
        scopes.append("admin")
    
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        user_id=user.id,
        email=user.email,
        hoTen=user.hoTen,
        vaiTro=user.vaiTro,
    )


@router.post("/login/oauth", response_model=Token)
async def login_oauth(
    db: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, để tương thích với các tiêu chuẩn OAuth2
    """
    nguoi_dung_service = NguoiDungService(db)
    user = await nguoi_dung_service.authenticate(
        email=form_data.username, password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
        )
    
    if not user.trangThai:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động",
        )
    
    # Tạo scopes dựa trên vai trò
    scopes = ["user"]
    if user.vaiTro == "admin":
        scopes.append("admin")
    
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    }


@router.post("/password-reset/request", response_model=ResponseSchema)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: SessionDep,
) -> Any:
    """
    Yêu cầu reset mật khẩu qua email
    """
    nguoi_dung_service = NguoiDungService(db)
    user = await nguoi_dung_service.get_by_email(email=reset_request.email)
    
    if user:
        # Tạo token cho reset mật khẩu
        reset_token = create_reset_password_token(user.email)
        
        # TODO: Gửi email ở đây với token
        # email_service.send_password_reset_email(user.email, reset_token)
        
        # Trong môi trường dev, trả về token để test
        if settings.ENV == "development":
            return ResponseSchema(
                success=True,
                message="Liên kết khôi phục mật khẩu đã được gửi đến email của bạn",
                data={"reset_token": reset_token}
            )
    
    return ResponseSchema(
        success=True,
        message="Nếu email tồn tại trong hệ thống, một liên kết khôi phục mật khẩu sẽ được gửi"
    )


@router.post("/password-reset/confirm", response_model=ResponseSchema)
async def reset_password(
    reset_data: NewPasswordRequest,
    db: SessionDep,
) -> Any:
    """
    Đặt lại mật khẩu với token hợp lệ
    """
    email = verify_reset_password_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token không hợp lệ hoặc đã hết hạn",
        )
    
    nguoi_dung_service = NguoiDungService(db)
    user = await nguoi_dung_service.get_by_email(email=email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại",
        )
    
    # Cập nhật mật khẩu
    user_update = {"matKhau": reset_data.password}
    await nguoi_dung_service.update(db_obj=user, obj_in=user_update)
    
    return ResponseSchema(
        success=True,
        message="Mật khẩu đã được đặt lại thành công"
    )


@router.get("/me", response_model=ResponseSchema)
async def read_current_user(
    current_user: CurrentUser,
) -> Any:
    """
    Lấy thông tin người dùng hiện tại
    """
    return ResponseSchema(
        success=True,
        message="Thông tin người dùng",
        data={
            "id": current_user.id,
            "email": current_user.email,
            "hoTen": current_user.hoTen,
            "vaiTro": current_user.vaiTro,
            "trangThai": current_user.trangThai,
            "toChucId": current_user.toChucId,
        }
    ) 