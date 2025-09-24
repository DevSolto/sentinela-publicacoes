from __future__ import annotations

import os
from functools import lru_cache
from typing import AsyncIterator

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

load_dotenv()


class MongoSettingsError(RuntimeError):
    """Erro lançado quando as variáveis de ambiente do MongoDB não estão configuradas."""


@lru_cache
def get_mongo_client() -> AsyncIOMotorClient:
    """Cria um cliente assíncrono do MongoDB utilizando as variáveis de ambiente."""
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise MongoSettingsError("Variável de ambiente MONGO_URI não definida.")

    max_pool_size = int(os.getenv("MONGO_MAX_POOL_SIZE", "20"))
    min_pool_size = int(os.getenv("MONGO_MIN_POOL_SIZE", "0"))
    server_selection_timeout_ms = int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT", "5000"))

    return AsyncIOMotorClient(
        uri,
        maxPoolSize=max_pool_size,
        minPoolSize=min_pool_size,
        serverSelectionTimeoutMS=server_selection_timeout_ms,
        tz_aware=True,
    )


def get_database(name: str | None = None) -> AsyncIOMotorDatabase:
    """Retorna o banco de dados configurado, validando o nome informado."""
    db_name = name or os.getenv("MONGO_DB_NAME")
    if not db_name:
        raise MongoSettingsError("Variável de ambiente MONGO_DB_NAME não definida.")

    client = get_mongo_client()
    return client[db_name]


@asynccontextmanager
async def lifespan_mongo_client() -> AsyncIterator[AsyncIOMotorClient]:
    """Gerencia o ciclo de vida do cliente MongoDB em aplicações assíncronas."""
    client = get_mongo_client()
    try:
        yield client
    finally:
        client.close()
