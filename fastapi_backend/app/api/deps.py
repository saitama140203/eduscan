from typing import Annotated, Generator, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password
from app.db.session import get_db
from app.models.nguoidung import NguoiDung
from app.schemas.token import TokenPayload, TokenData
from app.services.nguoidung import NguoiDungService


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scopes={
        "admin": "Quyền quản trị",
        "user": "Quyền người dùng tiêu chuẩn",
    },
)

# Dependency cơ bản cho DB
SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    security_scopes: SecurityScopes,
    db: SessionDep,
    token: str = Depends(oauth2_scheme),
) -> NguoiDung:
    """
    Lấy người dùng hiện tại từ token JWT
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(
            token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, user_id=user_id)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Kiểm tra phạm vi quyền
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Không đủ quyền. Yêu cầu quyền: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    # Lấy thông tin người dùng từ database
    nguoi_dung_service = NguoiDungService(db)
    user = await nguoi_dung_service.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[NguoiDung, Security(get_current_user, scopes=["user"])]
) -> NguoiDung:
    """
    Kiểm tra người dùng có active không
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động",
        )
    
    if not current_user.trangThai:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động",
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[NguoiDung, Security(get_current_user, scopes=["admin"])]
) -> NguoiDung:
    """
    Kiểm tra người dùng có quyền admin không
    """
    if current_user.vaiTro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yêu cầu quyền admin",
        )
    return current_user


CurrentUser = Annotated[NguoiDung, Depends(get_current_active_user)]
CurrentAdminUser = Annotated[NguoiDung, Depends(get_current_admin_user)] 