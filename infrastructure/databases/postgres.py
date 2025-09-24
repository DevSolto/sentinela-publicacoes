from __future__ import annotations

import os
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncIterator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()


class PostgresSettingsError(RuntimeError):
    """Erro lançado quando as variáveis de ambiente do Postgres não estão configuradas."""


def _should_echo_sql() -> bool:
    debug_flag = os.getenv("POSTGRES_ECHO", "false").lower()
    return debug_flag in {"1", "true", "t", "yes", "y"}


@lru_cache
def get_postgres_engine() -> AsyncEngine:
    """Cria um engine assíncrono do SQLAlchemy configurado para Postgres."""
    uri = os.getenv("POSTGRES_URI")
    if not uri:
        raise PostgresSettingsError("Variável de ambiente POSTGRES_URI não definida.")

    pool_size = int(os.getenv("POSTGRES_POOL_SIZE", "5"))
    max_overflow = int(os.getenv("POSTGRES_MAX_OVERFLOW", "10"))
    pool_timeout = int(os.getenv("POSTGRES_POOL_TIMEOUT", "30"))

    return create_async_engine(
        uri,
        echo=_should_echo_sql(),
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_pre_ping=True,
    )


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Retorna um factory de sessões assíncronas com commit explícito."""
    engine = get_postgres_engine()
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Context manager assíncrono que produz uma sessão transacional."""
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        yield session
