# infrastructure/sqlalchemy/database.py
"""
Единая точка инициализации SQLAlchemy (async).
"""

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Базовый класс моделей."""


# Приводим URL к async-схеме гарантированно
def _ensure_async_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        # на случай короткой формы
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    # оставим как есть — вдруг указали другой драйвер
    return url


ASYNC_DATABASE_URL: str = _ensure_async_url(settings.ASYNC_DATABASE_URL)

async_engine: AsyncEngine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# DI-зависимость для FastAPI
async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


def create_session_factory_no_pool() -> async_sessionmaker[AsyncSession]:
    """
    Создать фабрику AsyncSession с отдельным движком без пула соединений.
    Полезно для задач (например, Celery), где важно избежать конфликтов event loop.
    """
    # Локальный импорт, чтобы избежать проблем статического анализа окружения
    from sqlalchemy.pool import NullPool  # type: ignore

    isolated_engine: AsyncEngine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
        poolclass=NullPool,
    )
    return async_sessionmaker(
        bind=isolated_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
