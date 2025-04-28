# auth.py
from datetime import timedelta, datetime, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import User
from app.db.services import token_crud, user_crud
from app.schema.token import RefreshTokenCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)


async def generate_token_response(db: AsyncSession, user: User, expires_delta: Optional[timedelta] = None):
    access_token, access_token_expires = await create_jwt_token(user=user,
                                                                expires_delta=expires_delta)
    refresh_token, refresh_token_expires = await create_refresh_token(db, user.id)

    output_dict = {"access_token": access_token, "access_token_expiry": access_token_expires,
                   "refresh_token": refresh_token, "refresh_token_expiry": refresh_token_expires,
                   "token_type": "bearer"}
    return output_dict


async def create_jwt_token(user: User, expires_delta: Optional[timedelta] = None):
    token_data = {"sub": user.id, "organization_id": user.organization_id, "role": user.role.name}
    token = await create_access_token(token_data, expires_delta)
    return token


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, expire


async def create_refresh_token(db: AsyncSession, user_id: str):
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token = jwt.encode({"sub": str(user_id), "exp": expire}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    token_create = RefreshTokenCreate(token=token, expires_at=expire, user_id=user_id)
    await token_crud.create(db, token_create)
    return token, expire


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await user_crud.get_by_email(db, email)
    if user and await verify_password(password, user.password):
        return user
    return False


async def decode_token(token) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload
