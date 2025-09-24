"""Utilitário para registrar execuções de coleta no Postgres."""
from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import psycopg
from psycopg import Connection

from scrapy_service.logging_config import configure_structured_logging
from scrapy_service.utils.context import bind_run_id
from scrapy_service.utils.metrics import register_item

logger = logging.getLogger(__name__)


@dataclass
class RunMetadata:
    """Metadados mínimos necessários para iniciar uma execução."""

    profile_id: str
    janela_dias: int
    run_id: uuid.UUID = field(default_factory=uuid.uuid4)
    context: Dict[str, Any] = field(default_factory=dict)


class RunsLogger:
    """Gerencia o ciclo de vida de uma execução registrada no banco."""

    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn or os.getenv("POSTGRES_DSN")
        if not self._dsn:
            raise RuntimeError("POSTGRES_DSN não configurado")
        self._conn: Connection | None = None
        self._run_id: uuid.UUID | None = None
        self._items = 0
        self._started_at: datetime | None = None
        self._profile_id: Optional[str] = None
        self._context = None

    def __enter__(self) -> "RunsLogger":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc:
            self.fail(str(exc))
        else:
            self.finish()

    def start(self, metadata: RunMetadata) -> uuid.UUID:
        """Cria o registro inicial da execução."""

        configure_structured_logging()
        self._conn = psycopg.connect(self._dsn, autocommit=True)
        self._run_id = metadata.run_id
        self._profile_id = metadata.profile_id
        self._started_at = datetime.now(tz=timezone.utc)

        context = {"janela_dias": metadata.janela_dias, **metadata.context}
        self._context = bind_run_id(str(metadata.run_id))
        self._context.__enter__()
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO runs (id, profile_id, started_at, status, context, items_collected)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                ON CONFLICT (id) DO UPDATE SET
                    profile_id = EXCLUDED.profile_id,
                    started_at = EXCLUDED.started_at,
                    status = EXCLUDED.status,
                    context = EXCLUDED.context
                """,
                (
                    str(metadata.run_id),
                    metadata.profile_id,
                    self._started_at,
                    "running",
                    json.dumps(context),
                    0,
                ),
            )
        logger.info(
            "Execução iniciada",
            extra={"profile_id": metadata.profile_id, "janela_dias": metadata.janela_dias},
        )
        return metadata.run_id

    def increment_items(self, spider_name: str, amount: int = 1) -> None:
        """Incrementa o contador interno e emite métrica de coleta."""

        if amount < 1:
            return
        self._items += amount
        register_item(spider_name, amount)

    def finish(self, status: str = "finished") -> None:
        """Marca a execução como concluída com sucesso."""

        if not self._conn or not self._run_id:
            return
        finished_at = datetime.now(tz=timezone.utc)
        with self._conn.cursor() as cur:
            cur.execute(
                """
                UPDATE runs
                SET finished_at = %s,
                    status = %s,
                    items_collected = %s,
                    error_message = NULL
                WHERE id = %s
                """,
                (finished_at, status, self._items, str(self._run_id)),
            )
        logger.info(
            "Execução finalizada",
            extra={
                "profile_id": self._profile_id,
                "items": self._items,
                "status": status,
            },
        )
        self._cleanup()

    def fail(self, error_message: str) -> None:
        """Registra falha, mantendo o contador de itens coletados."""

        if not self._conn or not self._run_id:
            return
        finished_at = datetime.now(tz=timezone.utc)
        with self._conn.cursor() as cur:
            cur.execute(
                """
                UPDATE runs
                SET finished_at = %s,
                    status = %s,
                    items_collected = %s,
                    error_message = %s
                WHERE id = %s
                """,
                (finished_at, "failed", self._items, error_message[:2000], str(self._run_id)),
            )
        error = RuntimeError(error_message)
        logger.error(
            "Execução finalizada com erro",
            extra={
                "profile_id": self._profile_id,
                "items": self._items,
                "error": error_message,
            },
        )
        self._cleanup(error)

    def _cleanup(self, error: Optional[Exception] = None) -> None:
        if self._conn:
            self._conn.close()
        self._conn = None
        self._run_id = None
        self._items = 0
        self._profile_id = None
        self._started_at = None
        if self._context:
            if error:
                self._context.__exit__(error.__class__, error, None)
            else:
                self._context.__exit__(None, None, None)
            self._context = None


__all__ = ["RunsLogger", "RunMetadata"]
