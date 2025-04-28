from typing import Optional

from pydantic import BaseModel, EmailStr

from app.schema.organization import OrganizationOut
from app.schema.role import RoleOut


class UserBase(BaseModel):
    email: EmailStr
    organization_id: Optional[str] = None
    role_id: str
    name: str
    is_active: bool = True
    phone_number: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    id: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[str] = None


class UserOut(UserBase):
    id: str
    organization: Optional[OrganizationOut] = None
    role: RoleOut

    class Config:
        from_attributes = True
        
class ChangePasswordRequest(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    template_name: str = "default"

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_new_password: str

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True