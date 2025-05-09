from typing import Optional, List, Dict, Any, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, get_password_hash
from app.models.nguoidung import NguoiDung
from app.schemas.nguoidung import NguoiDungCreate, NguoiDungUpdate
from app.services.base import BaseService


class NguoiDungService(BaseService[NguoiDung, NguoiDungCreate, NguoiDungUpdate]):
    """
    Service xử lý logic liên quan đến NguoiDung
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, NguoiDung)
    
    async def get_by_email(self, email: str) -> Optional[NguoiDung]:
        """
        Tìm người dùng theo email
        """
        stmt = select(NguoiDung).where(NguoiDung.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[NguoiDung]:
        """
        Tìm người dùng theo tên đăng nhập
        """
        stmt = select(NguoiDung).where(NguoiDung.hoTen.ilike(f"%{name}%"))
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def authenticate(self,  email: str, password: str) -> Optional[NguoiDung]:
        """
        Xác thực người dùng bằng email và mật khẩu
        """
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.matKhau):
            return None
        return user
    
    async def create(self, obj_in: NguoiDungCreate) -> NguoiDung:
        """
        Tạo người dùng mới và hash mật khẩu
        """
        db_obj = NguoiDung(
            email=obj_in.email,
            hoTen=obj_in.hoTen,
            matKhau=get_password_hash(obj_in.matKhau),
            vaiTro=obj_in.vaiTro,
            toChucId=obj_in.toChucId,
            trangThai=True,  # Active = True
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        *,
        db_obj: NguoiDung,
        obj_in: Union[NguoiDungUpdate, Dict[str, Any]]
    ) -> NguoiDung:
        """
        Cập nhật thông tin người dùng, hash mật khẩu nếu được cung cấp
        """
        update_data = obj_in.model_dump(exclude_unset=True) if isinstance(obj_in, NguoiDungUpdate) else obj_in
        
        if "matKhau" in update_data and update_data["matKhau"]:
            update_data["matKhau"] = get_password_hash(update_data["matKhau"])
        
        return await super().update(db_obj=db_obj, obj_in=update_data)
    
    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> Optional[NguoiDung]:
        """
        Đổi mật khẩu người dùng
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        if not verify_password(current_password, user.matKhau):
            return None
        
        user.matKhau = get_password_hash(new_password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def activate(self, user_id: int) -> Optional[NguoiDung]:
        """
        Kích hoạt tài khoản người dùng
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        user.trangThai = True
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def deactivate(self, user_id: int) -> Optional[NguoiDung]:
        """
        Vô hiệu hóa tài khoản người dùng
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        user.trangThai = False
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user 