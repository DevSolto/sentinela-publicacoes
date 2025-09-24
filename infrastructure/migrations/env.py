from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection

from infrastructure.databases.postgres import get_postgres_engine
from infrastructure.models.postgres import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _database_url() -> str:
    url = os.getenv("POSTGRES_URI", "postgresql+asyncpg://postgres:postgres@localhost:5432/sentinela")
    return url


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa as migrações em modo offline."""
    url = _database_url().replace("+asyncpg", "")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa as migrações utilizando o engine assíncrono."""

    async def _run() -> None:
        connectable = get_postgres_engine()
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    asyncio.run(_run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
