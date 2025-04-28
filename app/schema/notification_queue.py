from typing import Optional

from pydantic import BaseModel

from app.core.enum import NotificationTypeEnum, NotificationStatusEnum


class NotificationQueueBase(BaseModel):
    recipient: str
    body: str
    status: NotificationStatusEnum
    notification_type: NotificationTypeEnum


class NotificationQueueCreate(NotificationQueueBase):
    subject: Optional[str] = None
    message: Optional[str] = None


class NotificationQueueUpdate(BaseModel):
    id: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[NotificationStatusEnum] = None
    notification_type: Optional[NotificationTypeEnum] = None
    message: Optional[str] = None


class NotificationQueueOut(NotificationQueueBase):
    id: str
    recipient: str
    subject: str
    body: str
    status: NotificationStatusEnum
    notification_type: NotificationTypeEnum
    message: Optional[str] = None

    class Config:
        from_attributes = True
