from __future__ import annotations

from decimal import Decimal
from typing import Mapping, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func

from infrastructure.models.postgres import Checkpoint, Metric

MetricInput = Mapping[str, tuple[float | int | Decimal, Optional[str]]]


class PostgresCheckpointRepository:
    """Repositório responsável por checkpoints e métricas no Postgres."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def registrar_checkpoint(
        self,
        run_id: UUID | str,
        name: str,
        cursor: Optional[str] = None,
        metrics: Optional[MetricInput] = None,
    ) -> Checkpoint:
        """Cria ou atualiza um checkpoint garantindo idempotência pela chave composta."""
        metrics = metrics or {}
        async with self._session_factory() as session:
            checkpoint_id = await self._upsert_checkpoint(session, run_id, name, cursor)
            if metrics:
                await self._upsert_metrics(session, checkpoint_id, metrics)
            await session.commit()
            return await self._load_checkpoint(session, checkpoint_id)

    async def _upsert_checkpoint(
        self,
        session: AsyncSession,
        run_id: UUID | str,
        name: str,
        cursor: Optional[str],
    ) -> int:
        stmt = (
            insert(Checkpoint)
            .values(run_id=run_id, name=name, cursor=cursor)
            .on_conflict_do_update(
                index_elements=[Checkpoint.__table__.c.run_id, Checkpoint.__table__.c.name],
                set_={"cursor": cursor, "recorded_at": func.now()},
            )
            .returning(Checkpoint.__table__.c.id)
        )
        result = await session.execute(stmt)
        checkpoint_id = result.scalar_one()
        return int(checkpoint_id)

    async def _upsert_metrics(
        self,
        session: AsyncSession,
        checkpoint_id: int,
        metrics: MetricInput,
    ) -> None:
        for metric_name, (raw_value, unit) in metrics.items():
            value = raw_value if isinstance(raw_value, Decimal) else Decimal(str(raw_value))
            stmt = (
                insert(Metric)
                .values(
                    checkpoint_id=checkpoint_id,
                    name=metric_name,
                    value=value,
                    unit=unit,
                )
                .on_conflict_do_update(
                    index_elements=[Metric.__table__.c.checkpoint_id, Metric.__table__.c.name],
                    set_={
                        "value": value,
                        "unit": unit,
                        "recorded_at": func.now(),
                    },
                )
            )
            await session.execute(stmt)

    async def _load_checkpoint(self, session: AsyncSession, checkpoint_id: int) -> Checkpoint:
        query = (
            select(Checkpoint)
            .options(selectinload(Checkpoint.metrics))
            .where(Checkpoint.__table__.c.id == checkpoint_id)
        )
        result = await session.execute(query)
        return result.scalar_one()
