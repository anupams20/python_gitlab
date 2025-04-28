from __future__ import annotations

from typing import AsyncGenerator, List

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from app.core.config import settings
from app.core.context import current_user
from app.core.enum import RoleEnum
from app.core.logging import AppLogger
from app.db.models import User
from app.db.services import user_crud
from app.db.session import AsyncSessionFactory, SyncSessionFactory
from app.schema.token import TokenData
from app.utils.auth import decode_token

logger = AppLogger().get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.ROOT_PATH}/users/login")


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        yield session


def get_sync_db() -> Session:
    with SyncSessionFactory() as session:
        return session


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await decode_token(token)
        user_id: str = payload.get("sub")
        organization_id: str = payload.get("organization_id")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, organization_id=organization_id)
    except JWTError:
        raise credentials_exception
    user = await user_crud.get(db, token_data.user_id)

    if not user:
        raise credentials_exception
    if user.organization_id != organization_id or user.role.name != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization or role mismatch",
        )
    if user:
        current_user.set(user)
    return user


async def check_roles(allowed_roles: List[RoleEnum], user: User = Depends(get_current_user)):
    role = user.role.name
    if RoleEnum(role) not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have the required role to access this resource",
        )


async def check_organization(expected_organization_id: str, user: User = Depends(get_current_user)):
    """Check if the user belongs to the required organization."""
    organization_id = user.organization_id
    if organization_id != expected_organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't belong to the required organization",
        )


async def check_role_and_organization(
    allowed_roles: List[RoleEnum],
    expected_organization_id: str,
    user: User = Depends(get_current_user),
):
    """Check if the user has the correct role and belongs to the required organization."""
    await check_roles(allowed_roles=allowed_roles, user=user)
    await check_organization(expected_organization_id, user)


async def get_user_crud():
    return user_crud

