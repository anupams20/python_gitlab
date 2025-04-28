# crud.py
from typing import Generic, Iterable, List, Optional, Protocol, Type, TypeVar
from app.core.enums import EventNameEnum
from fastapi import HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.base import Base
from app.db.models.user import User
from app.core.context import current_user

# Define types for Pydantic and SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic CRUD operations for any model"""

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        :param model: A SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.unique().scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Iterable[ModelType]:
        """Get multiple records."""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.unique().scalars().all()

    async def get_by_ids(self, db: AsyncSession, ids: List[str]):
        result = await db.execute(select(self.model).filter(self.model.id.in_(ids)))
        return result.unique().scalars().all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing record."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        db_obj = await self.get(db, obj_in.id)
        if not db_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        for field, value in obj_data.items():
            if value is not None:
                setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> ModelType:
        """Delete a record."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        db_obj = result.unique().scalar_one_or_none()

        if not db_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        await db.execute(sqlalchemy_delete(self.model).where(self.model.id == id))
        await db.commit()
        return db_obj
