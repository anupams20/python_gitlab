from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schema.pydantic_base import PydanticOutBase


class RefreshTokenBase(BaseModel):
    token: str
    expires_at: datetime
    user_id: str


class RefreshTokenCreate(RefreshTokenBase):
    pass


class RefreshTokenUpdate(BaseModel):
    token: Optional[str]
    expires_at: Optional[str]
    user_id: Optional[str]


class TokenOut(RefreshTokenBase):
    id: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    access_token_expiry: datetime
    refresh_token_expiry: datetime


class TokenData(BaseModel):
    user_id: str
    organization_id: str | None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
