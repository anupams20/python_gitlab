from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enum import RoleEnum
from app.db.models import Base


class Role(Base):
    name: Mapped[RoleEnum] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
