from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Sequence

import sqlalchemy as sa
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base declarativa compartilhada entre todos os modelos SQLAlchemy."""


class Profile(Base):
    """Perfil monitorado pela coleta de publicações."""

    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do perfil monitorado.",
    )
    username: Mapped[str] = mapped_column(
        sa.String(150),
        nullable=False,
        comment="Nome de usuário observado na plataforma.",
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        sa.String(255),
        nullable=True,
        comment="Nome completo disponibilizado pelo perfil.",
    )
    biography: Mapped[Optional[str]] = mapped_column(
        sa.Text(),
        nullable=True,
        comment="Descrição ou biografia configurada pelo perfil.",
    )
    external_url: Mapped[Optional[str]] = mapped_column(
        sa.String(255),
        nullable=True,
        comment="URL externa configurada no perfil.",
    )
    is_private: Mapped[bool] = mapped_column(
        sa.Boolean(),
        nullable=False,
        default=False,
        server_default=sa.false(),
        comment="Indica se o perfil é privado no momento da coleta.",
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Data de criação do registro do perfil.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data da última atualização do registro.",
    )

    runs: Mapped[list["Run"]] = relationship(
        "Run",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        sa.Index(
            "ix_profiles_username",
            "username",
            unique=True,
            postgresql_using="btree",
            comment="Garante unicidade e pesquisa eficiente pelo nome de usuário.",
        ),
    )


class Run(Base):
    """Execução de coleta agendada para um perfil."""

    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único da execução.",
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        comment="Referência ao perfil ao qual a execução pertence.",
    )
    started_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Momento em que a execução foi iniciada.",
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
        comment="Momento em que a execução foi concluída.",
    )
    status: Mapped[str] = mapped_column(
        sa.String(32),
        nullable=False,
        server_default=sa.text("'running'"),
        comment="Estado atual da execução (ex.: running, finished, failed).",
    )
    context: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Contexto adicional ou parâmetros utilizados na execução.",
    )
    items_collected: Mapped[int] = mapped_column(
        sa.Integer(),
        nullable=False,
        default=0,
        server_default=sa.text("0"),
        comment="Quantidade total de itens processados pela execução.",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        sa.Text(),
        nullable=True,
        comment="Mensagem de erro associada à execução, quando existente.",
    )

    profile: Mapped["Profile"] = relationship("Profile", back_populates="runs")
    checkpoints: Mapped[list["Checkpoint"]] = relationship(
        "Checkpoint",
        back_populates="run",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        sa.Index(
            "ix_runs_profile_status",
            "profile_id",
            "status",
            postgresql_using="btree",
            comment="Permite filtrar execuções por perfil e estado atual.",
        ),
        sa.Index(
            "ix_runs_started_at",
            "started_at",
            postgresql_using="btree",
            comment="Ordenação eficiente das execuções pela data de início.",
        ),
    )


class Checkpoint(Base):
    """Marca um ponto de controle dentro de uma execução."""

    __tablename__ = "checkpoints"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identificador sequencial do checkpoint.",
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
        comment="Execução à qual o checkpoint pertence.",
    )
    name: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        comment="Nome lógico do checkpoint dentro da execução.",
    )
    cursor: Mapped[Optional[str]] = mapped_column(
        sa.String(255),
        nullable=True,
        comment="Cursor, offset ou ponteiro utilizado para retomar a coleta.",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Momento de gravação ou atualização do checkpoint.",
    )

    run: Mapped["Run"] = relationship("Run", back_populates="checkpoints")
    metrics: Mapped[list["Metric"]] = relationship(
        "Metric",
        back_populates="checkpoint",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("run_id", "name", name="uq_checkpoints_run_name"),
        sa.Index(
            "ix_checkpoints_run_id",
            "run_id",
            postgresql_using="btree",
            comment="Facilita consultas de checkpoints por execução.",
        ),
    )


class Metric(Base):
    """Métrica numérica associada a um checkpoint."""

    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identificador sequencial da métrica registrada.",
    )
    checkpoint_id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        ForeignKey("checkpoints.id", ondelete="CASCADE"),
        nullable=False,
        comment="Checkpoint ao qual a métrica pertence.",
    )
    name: Mapped[str] = mapped_column(
        sa.String(120),
        nullable=False,
        comment="Nome da métrica registrada (ex.: posts_processados).",
    )
    value: Mapped[Decimal] = mapped_column(
        sa.Numeric(20, 4),
        nullable=False,
        comment="Valor numérico associado à métrica.",
    )
    unit: Mapped[Optional[str]] = mapped_column(
        sa.String(50),
        nullable=True,
        comment="Unidade de medida ou qualificador do valor.",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Momento em que a métrica foi registrada ou atualizada.",
    )

    checkpoint: Mapped["Checkpoint"] = relationship("Checkpoint", back_populates="metrics")

    __table_args__ = (
        UniqueConstraint("checkpoint_id", "name", name="uq_metrics_checkpoint_name"),
        sa.Index(
            "ix_metrics_checkpoint",
            "checkpoint_id",
            postgresql_using="btree",
            comment="Auxilia a recuperar todas as métricas de um checkpoint.",
        ),
    )


ModelsType = Sequence[type[Base]]
