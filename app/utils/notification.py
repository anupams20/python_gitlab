from datetime import datetime, timezone
from app.core.enum import NotificationTypeEnum, NotificationStatusEnum
from app.celery.tasks import send_notification
from app.celery.clickhouse import process_event
from app.core.deps import get_current_user
from app.core.enums import EventNameEnum
from app.db.models.user import User
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.services import notification_template_crud, notification_queue_crud
from app.schema.notification_queue import NotificationQueueCreate
from app.utils import jinja
from app.core.logging import AppLogger

logger = AppLogger().get_logger()

async def handle_send_notification(
    recipient_addr: str,
    db: AsyncSession,
    context: dict,
    template_name: str = None,
    body_template: str = None,
    subject: str = None,
    user: User = Depends(get_current_user)
):
    # Handle template or body_template
    if template_name is None and body_template is None:
        raise HTTPException(status_code=400, detail="Either template_name or body_template must be present")

    if template_name is not None:
        template = await notification_template_crud.get_by_name(db, name=template_name)
        if template is None:
            raise HTTPException(status_code=404, detail=f"Template with name '{template_name}' not found")
        body_template = template.body
        subject = template.subject

    # Render the email body with the template and context
    body = await jinja.render_template(body_template, context)

    # Create the notification in the queue
    notification_obj_in = NotificationQueueCreate(
        notification_type=NotificationTypeEnum.EMAIL,
        status=NotificationStatusEnum.QUEUED,
        recipient=recipient_addr,
        subject=subject,
        body=body
    )

    notification_db_obj = await notification_queue_crud.create(db, notification_obj_in)
    process_event.delay(
            name=EventNameEnum.NOTIFICATION_QUEUE_CREATE,
            payload=notification_db_obj.to_dict(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            org_id = user.organization_id,
            user_id = user.id
    )
    # Trigger the notification to be sent asynchronously
    send_notification.delay(notification_db_obj.id)