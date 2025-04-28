import os
from typing import Annotated, Any

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    PostgresDsn,
    TypeAdapter,
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    BROKER_PROTOCOL: str = "amqp"
    BROKER_USER: str
    BROKER_PASSWORD: str
    BROKER_HOST: str
    BROKER_PORT: str
    BROKER_VHOST: str


    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USERNAME: str
    CLICKHOUSE_PASSWORD: str
    CLICKHOUSE_DATABASE: str

    SCHEME: str = "http"

    # MAILJET_API_KEY: str
    # MAILJET_API_SECRET: str
    # SENDER_EMAIL: EmailStr = TypeAdapter(EmailStr).validate_strings("prasanna@beehyv.com")

    ROOT_PATH: str = ""

    PROMETHEUS_COLLECTION_PORT: int = 8001

    JAEGER_URL: str

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    PATH_TO_TEMP: str = "/temp"

    SUPER_ADMIN_EMAIL: str
    SUPER_ADMIN_USERNAME: str
    SUPER_ADMIN_PASSWORD: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI_SYNC(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
os.environ["PGVECTOR_CONNECTION_STRING"] = str(settings.SQLALCHEMY_DATABASE_URI_SYNC)
