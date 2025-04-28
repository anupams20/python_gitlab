from typing import Optional

from pydantic import BaseModel

from app.core.enum import RoleEnum


class RoleBase(BaseModel):
    name: RoleEnum


class RoleCreate(RoleBase):
    description: Optional[str]


class RoleUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[RoleEnum] = None
    description: Optional[str] = None


class RoleOut(RoleBase):
    id: str
    name: RoleEnum
    description: Optional[str]

    class Config:
        from_attributes = True
