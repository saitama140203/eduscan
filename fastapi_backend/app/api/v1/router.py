from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    tochuc, 
    nguoidung, 
    lophoc, 
    hocsinh, 
    mauphieu, 
    baikiemtra, 
    phieutraloi, 
    caidat
)

# Tạo router chính cho API v1
router = APIRouter()

# Đăng ký các router endpoint
router.include_router(auth.router, prefix="/auth", tags=["xác thực"])
router.include_router(tochuc.router, prefix="/tochuc", tags=["tổ chức"])
router.include_router(nguoidung.router, prefix="/nguoidung", tags=["người dùng"])
router.include_router(lophoc.router, prefix="/lophoc", tags=["lớp học"])
router.include_router(hocsinh.router, prefix="/hocsinh", tags=["học sinh"])
router.include_router(mauphieu.router, prefix="/mauphieu", tags=["mẫu phiếu"])
router.include_router(baikiemtra.router, prefix="/baikiemtra", tags=["bài kiểm tra"])
router.include_router(phieutraloi.router, prefix="/phieutraloi", tags=["phiếu trả lời"])
router.include_router(caidat.router, prefix="/caidat", tags=["cài đặt"]) 