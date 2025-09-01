# migrations/alembic/env.py
"""
Alembic (async) конфигурация:

"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# Логгирование alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Импортируем единую метадату
from core.config import get_settings  # noqa: E402
from infrastructure.sqlalchemy.database import Base  # noqa: E402
# Важно: импортируем модели, чтобы Base.metadata содержала все таблицы для autogenerate
from infrastructure.sqlalchemy import models  # noqa: F401,E402

# Важно: чтобы метадата включала все модели, они должны быть импортированы где-то до обращения к Base.metadata
# Если модели объявлены в отдельных модулях – простого импорта достаточно:
# from infrastructure.sqlalchemy import models  # noqa: F401

target_metadata = Base.metadata


def _async_url() -> str:
    settings = get_settings()
    return settings.ASYNC_DATABASE_URL


def _sync_url_for_offline(async_url: str) -> str:
    """
    Для offline режима alembic лучше указывать sync-URL (без +asyncpg).
    """
    if async_url.startswith("postgresql+asyncpg://"):
        return async_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if async_url.startswith("postgres://"):
        return async_url.replace("postgres://", "postgresql://", 1)
    return async_url


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме (без подключения к БД)."""
    url = _sync_url_for_offline(_async_url())
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме через AsyncEngine."""
    connectable: AsyncEngine = create_async_engine(_async_url(), future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
