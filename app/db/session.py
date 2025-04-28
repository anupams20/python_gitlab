from sqlalchemy import create_engine, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine_async = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True, echo=True, future=True, poolclass=NullPool)
AsyncSessionFactory = async_sessionmaker(
    bind=engine_async,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

engine_sync = create_engine(str(settings.SQLALCHEMY_DATABASE_URI_SYNC), echo=True)
SyncSessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)
