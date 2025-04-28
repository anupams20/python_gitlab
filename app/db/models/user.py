from __future__ import annotations

from typing import List

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base


class User(Base):
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role_id: Mapped[str] = mapped_column(String, ForeignKey("role.id"))
    role: Mapped["Role"] = relationship("Role", lazy="joined", innerjoin=True)

    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organization.id"), nullable=True
    )
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="users", lazy="selectin"
    )

    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user"
    )
