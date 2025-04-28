from typing import Optional

from pydantic import BaseModel

from app.schema.pydantic_base import PydanticOutBase


class OrganizationBase(BaseModel):
    name: str


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    id: str
    name: Optional[str]


class OrganizationOut(OrganizationBase):
    id: str

    class Config:
        from_attributes = True
