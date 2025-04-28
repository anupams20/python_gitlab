from typing import List

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.services import CRUDBase
from app.schema.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User:
        result = await db.execute(select(self.model).filter(self.model.email == email))
        return result.scalar_one_or_none()

    async def get_all_users(self, db: AsyncSession, organization_id: str, skip: int = 0, limit: int = 10) -> List[User]:
        result = await db.execute(select(self.model).filter(self.model.organization_id == organization_id).offset(skip).limit(limit))
        return result.scalars().fetchall()

user_crud = CRUDUser(User)
