from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base


class Organization(Base):
    name: Mapped[str] = mapped_column(String, unique=True, index=True)

    # One-to-many relationship: One organization can have multiple users
    users: Mapped[List["User"]] = relationship("User", back_populates="organization")