"""create core tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20240405_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="Identificador único do perfil monitorado."),
        sa.Column("username", sa.String(length=150), nullable=False, comment="Nome de usuário observado na plataforma."),
        sa.Column("full_name", sa.String(length=255), nullable=True, comment="Nome completo disponibilizado pelo perfil."),
        sa.Column("biography", sa.Text(), nullable=True, comment="Descrição ou biografia configurada pelo perfil."),
        sa.Column("external_url", sa.String(length=255), nullable=True, comment="URL externa configurada no perfil."),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default=sa.text("false"), comment="Indica se o perfil é privado no momento da coleta."),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="Data de criação do registro do perfil."),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="Data da última atualização do registro."),
        sa.PrimaryKeyConstraint("id", name="pk_profiles"),
    )
    op.create_index(
        "ix_profiles_username",
        "profiles",
        ["username"],
        unique=True,
        postgresql_using="btree",
    )
    op.execute(sa.text("COMMENT ON INDEX ix_profiles_username IS 'Garante unicidade e pesquisa eficiente pelo nome de usuário.'"))

    op.create_table(
        "runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="Identificador único da execução."),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False, comment="Referência ao perfil ao qual a execução pertence."),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="Momento em que a execução foi iniciada."),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True, comment="Momento em que a execução foi concluída."),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'running'"), comment="Estado atual da execução (ex.: running, finished, failed)."),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Contexto adicional ou parâmetros utilizados na execução."),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], name="fk_runs_profile_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_runs"),
    )
    op.create_index(
        "ix_runs_profile_status",
        "runs",
        ["profile_id", "status"],
        unique=False,
        postgresql_using="btree",
    )
    op.execute(sa.text("COMMENT ON INDEX ix_runs_profile_status IS 'Permite filtrar execuções por perfil e estado atual.'"))
    op.create_index(
        "ix_runs_started_at",
        "runs",
        ["started_at"],
        unique=False,
        postgresql_using="btree",
    )
    op.execute(sa.text("COMMENT ON INDEX ix_runs_started_at IS 'Ordenação eficiente das execuções pela data de início.'"))

    op.create_table(
        "checkpoints",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="Identificador sequencial do checkpoint."),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False, comment="Execução à qual o checkpoint pertence."),
        sa.Column("name", sa.String(length=100), nullable=False, comment="Nome lógico do checkpoint dentro da execução."),
        sa.Column("cursor", sa.String(length=255), nullable=True, comment="Cursor, offset ou ponteiro utilizado para retomar a coleta."),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="Momento de gravação ou atualização do checkpoint."),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], name="fk_checkpoints_run_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_checkpoints"),
        sa.UniqueConstraint("run_id", "name", name="uq_checkpoints_run_name"),
    )
    op.create_index(
        "ix_checkpoints_run_id",
        "checkpoints",
        ["run_id"],
        unique=False,
        postgresql_using="btree",
    )
    op.execute(sa.text("COMMENT ON INDEX ix_checkpoints_run_id IS 'Facilita consultas de checkpoints por execução.'"))

    op.create_table(
        "metrics",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="Identificador sequencial da métrica registrada."),
        sa.Column("checkpoint_id", sa.BigInteger(), nullable=False, comment="Checkpoint ao qual a métrica pertence."),
        sa.Column("name", sa.String(length=120), nullable=False, comment="Nome da métrica registrada (ex.: posts_processados)."),
        sa.Column("value", sa.Numeric(precision=20, scale=4), nullable=False, comment="Valor numérico associado à métrica."),
        sa.Column("unit", sa.String(length=50), nullable=True, comment="Unidade de medida ou qualificador do valor."),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="Momento em que a métrica foi registrada ou atualizada."),
        sa.ForeignKeyConstraint(["checkpoint_id"], ["checkpoints.id"], name="fk_metrics_checkpoint_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_metrics"),
        sa.UniqueConstraint("checkpoint_id", "name", name="uq_metrics_checkpoint_name"),
    )
    op.create_index(
        "ix_metrics_checkpoint",
        "metrics",
        ["checkpoint_id"],
        unique=False,
        postgresql_using="btree",
    )
    op.execute(sa.text("COMMENT ON INDEX ix_metrics_checkpoint IS 'Auxilia a recuperar todas as métricas de um checkpoint.'"))



def downgrade() -> None:
    op.drop_index("ix_metrics_checkpoint", table_name="metrics")
    op.drop_table("metrics")
    op.drop_index("ix_checkpoints_run_id", table_name="checkpoints")
    op.drop_table("checkpoints")
    op.drop_index("ix_runs_started_at", table_name="runs")
    op.drop_index("ix_runs_profile_status", table_name="runs")
    op.drop_table("runs")
    op.drop_index("ix_profiles_username", table_name="profiles")
    op.drop_table("profiles")
