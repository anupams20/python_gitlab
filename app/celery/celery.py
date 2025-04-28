from celery import Celery

from app.core.config import settings
from app.core.logging import AppLogger

logger = AppLogger().get_logger()


def create_celery_app():
    broker_connection_url = f"{settings.BROKER_PROTOCOL}://{settings.BROKER_USER}:{settings.BROKER_PASSWORD}@{settings.BROKER_HOST}:{settings.BROKER_PORT}/{settings.BROKER_VHOST}"
    db_backend = f"db+postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    app = Celery("worker", backend=db_backend, include=["app.celery.tasks"], broker=broker_connection_url)
    app.config_from_object('app.celery.celeryconfig')
    return app


celery_app = create_celery_app()
