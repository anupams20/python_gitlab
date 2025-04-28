from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enum import NotificationStatusEnum, NotificationTypeEnum
from app.db.models import Base


class NotificationQueue(Base):
    recipient: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[NotificationStatusEnum] = mapped_column(String, nullable=False,
                                                           default=NotificationStatusEnum.QUEUED)
    notification_type: Mapped[NotificationTypeEnum] = mapped_column(String, nullable=False,
                                                                    default=NotificationTypeEnum.EMAIL)

    message: Mapped[str] = mapped_column(Text, nullable=True)
