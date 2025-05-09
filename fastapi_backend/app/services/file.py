import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from typing import Optional

from app.core.config import settings


class FileService:
    """
    Service xử lý các thao tác với file
    """
    
    async def upload_logo(
        self, 
        file: UploadFile,
        to_chuc_id: int,
        nguoi_dung_id: int
    ) -> str:
        """
        Upload logo cho tổ chức và trả về đường dẫn
        """
        # Kiểm tra định dạng file
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.svg']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Định dạng file không được hỗ trợ. Chỉ chấp nhận JPG, JPEG, PNG hoặc SVG.")
        
        # Tạo tên file mới để tránh trùng lặp
        unique_filename = f"logo_{to_chuc_id}_{uuid.uuid4().hex}{file_extension}"
        
        # Tạo đường dẫn đến thư mục lưu trữ
        storage_path = settings.UPLOAD_DIR / "logos"
        os.makedirs(storage_path, exist_ok=True)
        
        # Đường dẫn đầy đủ đến file
        file_path = storage_path / unique_filename
        
        # Lưu file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi lưu file: {str(e)}")
        
        # Trả về đường dẫn tương đối để lưu vào database
        relative_path = f"/uploads/logos/{unique_filename}"
        
        # TODO: Lưu thông tin file vào bảng TapTin nếu cần
        
        return relative_path
    
    async def upload_avatar(
        self, 
        file: UploadFile,
        nguoi_dung_id: int
    ) -> str:
        """
        Upload ảnh đại diện cho người dùng và trả về đường dẫn
        """
        # Kiểm tra định dạng file
        allowed_extensions = ['.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Định dạng file không được hỗ trợ. Chỉ chấp nhận JPG, JPEG hoặc PNG.")
        
        # Tạo tên file mới để tránh trùng lặp
        unique_filename = f"avatar_{nguoi_dung_id}_{uuid.uuid4().hex}{file_extension}"
        
        # Tạo đường dẫn đến thư mục lưu trữ
        storage_path = settings.UPLOAD_DIR / "avatars"
        os.makedirs(storage_path, exist_ok=True)
        
        # Đường dẫn đầy đủ đến file
        file_path = storage_path / unique_filename
        
        # Lưu file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi lưu file: {str(e)}")
        
        # Trả về đường dẫn tương đối để lưu vào database
        relative_path = f"/uploads/avatars/{unique_filename}"
        
        # TODO: Lưu thông tin file vào bảng TapTin nếu cần
        
        return relative_path
    
    async def upload_document(
        self, 
        file: UploadFile,
        nguoi_dung_id: int,
        loai_document: str = "general"
    ) -> str:
        """
        Upload tài liệu như đề thi, bài tập và trả về đường dẫn
        """
        # Kiểm tra định dạng file
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Định dạng file không được hỗ trợ.")
        
        # Tạo tên file mới để tránh trùng lặp
        unique_filename = f"{loai_document}_{uuid.uuid4().hex}{file_extension}"
        
        # Tạo đường dẫn đến thư mục lưu trữ
        storage_path = settings.UPLOAD_DIR / "documents" / loai_document
        os.makedirs(storage_path, exist_ok=True)
        
        # Đường dẫn đầy đủ đến file
        file_path = storage_path / unique_filename
        
        # Lưu file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi lưu file: {str(e)}")
        
        # Trả về đường dẫn tương đối để lưu vào database
        relative_path = f"/uploads/documents/{loai_document}/{unique_filename}"
        
        return relative_path
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Xóa file theo đường dẫn
        """
        if not file_path:
            return False
        
        # Lấy đường dẫn tuyệt đối từ đường dẫn tương đối
        if file_path.startswith("/uploads/"):
            absolute_path = settings.UPLOAD_DIR / file_path[9:]  # Bỏ "/uploads/"
        else:
            return False
        
        try:
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                return True
        except Exception:
            return False
        
        return False 