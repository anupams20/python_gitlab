
from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.models import NotificationTemplate
from app.db.services import CRUDBase
from app.schema.notification_template import NotificationTemplateCreate, NotificationTemplateUpdate


class CRUDNotificationTemplate(CRUDBase[NotificationTemplate, NotificationTemplateCreate, NotificationTemplateUpdate]):

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[NotificationTemplate]:
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalar_one_or_none()


notification_template_crud = CRUDNotificationTemplate(NotificationTemplate)