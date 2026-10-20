"""Persistência operacional e particionamento mensal de medições."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "002_operational"
down_revision = "001_identity"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("alvos", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nome", sa.String(100), nullable=False), sa.Column("host", sa.String(253), nullable=False),
        sa.Column("porta", sa.Integer(), nullable=False), sa.Column("kind", sa.String(10), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("porta BETWEEN 1 AND 65535"), sa.CheckConstraint("kind IN ('tcp','http','https')"))
    op.create_table("medicoes", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ts", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("alvo_id", sa.String(36), sa.ForeignKey("alvos.id"), nullable=False),
        sa.Column("sucesso", sa.Boolean(), nullable=False), sa.Column("latencia_ms", sa.Float()),
        sa.CheckConstraint("latencia_ms IS NULL OR latencia_ms >= 0"), postgresql_partition_by="RANGE (ts)")
    op.create_index("ix_medicoes_alvo_ts", "medicoes", ["alvo_id", "ts"])
    op.create_table("medicoes_agregadas",
        sa.Column("alvo_id", sa.String(36), sa.ForeignKey("alvos.id"), primary_key=True),
        sa.Column("periodo", sa.String(10), primary_key=True),
        sa.Column("ts", sa.DateTime(timezone=True), primary_key=True),
        *[sa.Column(k, sa.BigInteger(), nullable=False) for k in ("total", "sucessos", "latencia_n")],
        sa.Column("latencia_soma", sa.Float(), nullable=False),
        sa.Column("latencia_min", sa.Float()), sa.Column("latencia_max", sa.Float()),
        sa.CheckConstraint("periodo IN ('minute','hour')"))
    op.create_table("incidentes", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("alvo_id", sa.String(36), sa.ForeignKey("alvos.id"), nullable=False),
        sa.Column("tipo", sa.String(40), nullable=False), sa.Column("severidade", sa.String(2), nullable=False),
        sa.Column("detectado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reconhecido_em", sa.DateTime(timezone=True)), sa.Column("resolvido_em", sa.DateTime(timezone=True)),
        sa.CheckConstraint("severidade IN ('P1','P2','P3')"))
    op.create_index("ix_incidentes_alvo_id", "incidentes", ["alvo_id"])
    op.create_index("uq_incidente_ativo", "incidentes", ["alvo_id", "tipo"], unique=True,
                    postgresql_where=sa.text("resolvido_em IS NULL"))
    for name in ("aprovacoes", "execucoes_runbook", "detectores"):
        op.create_table(name, sa.Column("id", sa.String(100), primary_key=True),
            sa.Column("documento", JSONB(), nullable=False), sa.Column("versao", sa.Integer(), nullable=False),
            sa.Column("estado", sa.String(32), nullable=False),
            sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False))
        op.create_index(f"ix_{name}_estado", name, ["estado"])
    op.create_table("slo", sa.Column("alvo_id", sa.String(36), sa.ForeignKey("alvos.id"), primary_key=True),
        sa.Column("alvo_pct", sa.Float(), nullable=False), sa.Column("janela_dias", sa.Integer(), nullable=False),
        sa.CheckConstraint("alvo_pct > 0 AND alvo_pct < 100"), sa.CheckConstraint("janela_dias > 0"))
    op.create_table("eventos_operacionais", sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False), sa.Column("ator", sa.String(100), nullable=False),
        sa.Column("acao", sa.String(80), nullable=False), sa.Column("recurso", sa.String(100), nullable=False),
        sa.Column("detalhes", JSONB(), nullable=False))
    op.create_index("ix_eventos_operacionais_ts", "eventos_operacionais", ["ts"])


def downgrade():
    for name in ("eventos_operacionais", "slo", "detectores", "execucoes_runbook", "aprovacoes",
                 "incidentes", "medicoes_agregadas", "medicoes", "alvos"):
        op.drop_table(name)
