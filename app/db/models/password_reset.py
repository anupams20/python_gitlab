from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta, timezone
from app.db.models import Base

class PasswordResetToken(Base):
    user_id: Mapped[str] = mapped_column(String, ForeignKey("user.id"), nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __init__(self, user_id: str, token: str, expires_at: datetime = None, expires_in: int = 3600):
        self.user_id = user_id
        self.token = token
        if expires_at is not None:
            self.expires_at = expires_at
        else:
            self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
