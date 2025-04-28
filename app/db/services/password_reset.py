from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.password_reset import PasswordResetToken
from datetime import datetime, timezone
from fastapi import HTTPException

async def create_password_reset_token(db: AsyncSession, user_id: str, token: str, expires_at: datetime):
    expires_at_naive = expires_at.replace(tzinfo=None)  # Ensure datetime is naive
    reset_token = PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at_naive)
    db.add(reset_token)
    await db.commit()
    await db.refresh(reset_token)
    return reset_token

async def get_password_reset_token(db: AsyncSession, token: str):
    reset_token = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == token)
    )
    reset_token = reset_token.scalars().first()

    if not reset_token:
        raise HTTPException(status_code=404, detail="Invalid token")

    if reset_token.is_used:
        raise HTTPException(status_code=400, detail="Token has already been used")

    expires_at_aware = reset_token.expires_at.replace(tzinfo=timezone.utc)

    # Check if the token is expired
    if datetime.now(timezone.utc) > expires_at_aware:
        raise HTTPException(status_code=400, detail="Token has expired")

    return reset_token

async def mark_token_as_used(db: AsyncSession, token: str):
    reset_token = await get_password_reset_token(db, token)
    if reset_token:
        reset_token.is_used = True
        await db.commit()
        await db.refresh(reset_token)
    return reset_token