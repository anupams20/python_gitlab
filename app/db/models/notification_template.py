from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import Base


class NotificationTemplate(Base):
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)