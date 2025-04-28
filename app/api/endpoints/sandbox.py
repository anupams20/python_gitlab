from datetime import datetime, timezone
import json
import traceback
import os
import shutil
from typing import Optional, Dict

from app.celery.clickhouse import process_event
from app.core.enums import EventNameEnum
from fastapi import APIRouter, UploadFile, HTTPException
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.celery.tasks import send_notification
from app.core import deps
from app.core.config import settings
from app.core.deps import get_current_user
from app.core.enum import NotificationTypeEnum, NotificationStatusEnum
from app.core.logging import AppLogger
from app.db.models import User
from app.db.services import notification_template_crud, notification_queue_crud
from app.schema.notification_queue import NotificationQueueCreate
from app.utils import jinja

router = APIRouter()
logger = AppLogger().get_logger()

@router.post("/send-test-email")
async def send_test_email(recipient_addr: EmailStr, from_addr: EmailStr, subject: str,
                          body_template: Optional[str] = None, template_id: Optional[str] = None,
                          context: Optional[Dict[str, str]] = None, db: AsyncSession = Depends(deps.get_db),
                          user: User = Depends(get_current_user)):
    try:
        if template_id is None and body_template is None:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                 detail="Either of template_id or body_template must be present")

        if template_id is not None:
            template = await notification_template_crud.get(db, template_id)
            body_template = template.body
        body = await jinja.render_template(body_template, context)
        notification_obj_in = NotificationQueueCreate(notification_type=NotificationTypeEnum.EMAIL,
                                                      status=NotificationStatusEnum.QUEUED, recipient=recipient_addr,
                                                      subject=subject, body=body)
        notification_db_obj = await notification_queue_crud.create(db, notification_obj_in)

        send_notification.delay(notification_db_obj.id)
        process_event.delay(
                name=EventNameEnum.NOTIFICATION_QUEUE_CREATE,
                payload=notification_db_obj.to_dict(),
                timestamp=datetime.now(timezone.utc).isoformat(),
                org_id = user.organization_id,
                user_id = user.id
            )
        return {"message": "Email Queued"}
    except Exception as e:
        stacktrace = traceback.format_exc()
        logger.error(json.dumps(stacktrace))
        raise e
