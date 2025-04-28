from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RefreshToken
from app.db.services import CRUDBase
from app.schema.token import RefreshTokenUpdate, RefreshTokenCreate


class CRUDToken(CRUDBase[RefreshToken, RefreshTokenCreate, RefreshTokenUpdate]):
    async def get_valid_token(self, db: AsyncSession, token: str, user_id: str) -> RefreshToken:
        stored_token = await db.execute(select(self.model).filter(
            self.model.token == token and self.model.user_id == user_id and self.model.expires_at > datetime.now(
                timezone.utc)))
        stored_token = stored_token.scalar_one_or_none()
        if not stored_token:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        return stored_token


token_crud = CRUDToken(RefreshToken)
