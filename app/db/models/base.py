import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql.sqltypes import DateTime, String

from app.core.logging import AppLogger

logger = AppLogger().get_logger()


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda _: str(uuid.uuid4()))

    additional_info: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[str] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True,
                                                 default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True,
                                                 onupdate=func.now(),
                                                 default=func.now())
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __str__(self):
        return f"{self.__tablename__}:{self.id}"

    def __repr__(self):
        try:
            return f"{self.__class__.__name__}({self.__tablename__}:{self.id})"
        except Exception:
            logger.error(f"Faulty-{self.__class__.__name__}")
            return f"Faulty-{self.__class__.__name__}"

    def to_dict(self):
            return {column.name: getattr(self, column.name) for column in self.__table__.columns}