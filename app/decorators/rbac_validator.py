from functools import wraps
from typing import List

from fastapi import Depends

from app.core.deps import check_roles, get_current_user
from app.core.enum import RoleEnum
from app.db.models import User


def rbac_validator(allowed_roles: List[RoleEnum]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: User = Depends(get_current_user), **kwargs):
            if user.role.name != RoleEnum.SUPER_ADMIN.value:
                await check_roles(allowed_roles=allowed_roles, user=user)
            return await func(*args, user=user, **kwargs)

        return wrapper

    return decorator
