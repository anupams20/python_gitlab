from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List

import httpx

from app.celery.celery import celery_app
from app.core import deps
from app.core.config import settings
from app.core.deps import get_db
from app.core.enum import NotificationStatusEnum
from app.core.logging import AppLogger
from app.db.models import NotificationQueue, User
from app.db.services import (
    notification_queue_crud,
)
from app.notification.email import MailjetProvider
from app.schema.notification_queue import NotificationQueueOut
from app.utils.email import EmailService
from app.core.enums import EventNameEnum
from datetime import datetime, timezone
from app.celery.clickhouse import process_event
logger = AppLogger().get_logger()


# `bind=True` adds task details to the task itself.


@celery_app.task(bind=True, retry_backoff=True, max_retries=3)
async def sample_task(self, x, y):
    try:
        logger.info(f"Within Task: {x}, {y}")
        return x + y
    except Exception as e:
        self.retry(exc=e, countdown=settings.RETRY_AFTER)


@celery_app.task(bind=True, retry_backoff=True, max_retries=3)
def send_notification(self, notification_queue_id: str, loop=asyncio.get_event_loop()):
    try:
        db_obj = deps.get_db()

        db = loop.run_until_complete(db_obj.__anext__())
        queue_obj: NotificationQueue = loop.run_until_complete(notification_queue_crud.get(db, notification_queue_id))
        try:
            logger.info("Within Task Send mail")
            provider = MailjetProvider()
            mail_service = EmailService(provider=provider)
            loop.run_until_complete(
                mail_service.send_email(
                    subject=queue_obj.subject,
                    recipient=queue_obj.recipient,
                    body=queue_obj.body,
                )
            )
            queue_obj.status = NotificationStatusEnum.SENT
        except Exception as e:
            queue_obj.status = NotificationStatusEnum.FAILED
            queue_obj.message = str(e)
            logger.error(str(e))
            self.retry(exc=e, countdown=settings.RETRY_AFTER)
        finally:
            loop.run_until_complete(notification_queue_crud.update(db, NotificationQueueOut.model_validate(queue_obj)))
    except Exception as e:
        logger.error(str(e))
        self.retry(exc=e, countdown=settings.RETRY_AFTER)

