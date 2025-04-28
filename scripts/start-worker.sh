#!/bin/sh
celery -A app.celery.celery.celery_app worker --loglevel=INFO --concurrency=4 --pool=gevent --pidfile=./worker.pid