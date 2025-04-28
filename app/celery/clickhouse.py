from __future__ import annotations

from app.celery.celery import celery_app
from app.core.logging import AppLogger
from datetime import datetime , timezone
from app.utils.clickhouse_client import client
from app.core.enums import EventNameEnum

logger = AppLogger().get_logger()

@celery_app.task(bind=True, retry_backoff=True, max_retries=3)
def process_event(self, name: EventNameEnum, payload: dict, timestamp: str, org_id: str=None, user_id: str=None):
    try:
        if client is None:
            raise ConnectionError("ClickHouse client is not initialized")

        # Log the payload to check its structure
        logger.info(f"Processing event: {name} payload: {payload}")

        if not payload:
            logger.error("Payload is empty")
            return {"status": "error", "message": "Payload is empty"}

        client_timestamp = datetime.fromisoformat(timestamp)
        server_timestamp = datetime.now(timezone.utc)

        data = [
            [name.value, org_id, user_id, payload, client_timestamp, server_timestamp]
        ]

        # Log the data before inserting
        logger.info(f"Data being inserted: {data}")

        client.command('SET async_insert = 1, wait_for_async_insert = 1')

        if not data:
            logger.error("No data to insert into ClickHouse")
            return {"status": "error", "message": "No data to insert"}

        # Insert data
        client.insert(
            'events',
            data=data,
            column_names=['name', 'organization_id', 'user_id', 'payload', 'client_timestamp', 'server_timestamp']
        )

        return {"status": "success", "event_name": name.value}

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        self.retry(exc=e, countdown=60)