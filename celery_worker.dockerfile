FROM python:3.11-alpine

RUN apk --no-cache add  gcc libpq-dev linux-headers musl-dev python3-dev geos geos-dev ffmpeg \
    && addgroup -S appgroup && adduser -S appuser -G appgroup \
    && pip install poetry \
    &&  geos-config --cflags

ENV CFLAGS="-Wno-error=incompatible-pointer-types"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /code/
ENV PYTHONPATH=/code

COPY pyproject.toml /code/
COPY poetry.lock /code/
COPY  app /code/app
COPY migrations /code/migrations
COPY alembic.ini /code/
COPY gunicorn_conf.py /code/
COPY scripts/start-worker.sh /code/start-worker.sh

RUN mkdir -p /code/gunicorn_temp && chown -R appuser:appgroup /code \
# Project initialization:
&& poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi \
    && chmod +x /code/start-worker.sh

# Switch to the non-root user
USER appuser

CMD [ "sh", "/code/start-worker.sh" ]
