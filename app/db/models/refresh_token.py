from datetime import datetime

from sqlalchemy import String, ForeignKey, UUID, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base


class RefreshToken(Base):
    token: Mapped[str] = mapped_column(String, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("user.id"))
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens", lazy="selectin")