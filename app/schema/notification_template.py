from typing import Optional

from pydantic import BaseModel


class NotificationTempalateBase(BaseModel):
    name: str
    body: str


class NotificationTemplateCreate(NotificationTempalateBase):
    subject: Optional[str]


class NotificationTemplateUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None


class NotificationTemplateOut(NotificationTempalateBase):
    id: str
    name: str
    subject: Optional[str]
    body: str

    class Config:
        from_attributes = True
