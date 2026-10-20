"""Configuração da coleta por alvo.

Revision ID: 003_collection
Revises: 002_operational
"""
from alembic import op
import sqlalchemy as sa

revision = "003_collection"
down_revision = "002_operational"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_eventos_incidentes_id", "eventos_operacionais", ["id"],
        postgresql_where=sa.text("acao IN ('incident.created','incident.ack','incident.resolve')"))
    op.add_column("alvos", sa.Column("intervalo_s", sa.Float(), nullable=False, server_default="1"))
    op.add_column("alvos", sa.Column("timeout_s", sa.Float(), nullable=False, server_default="1"))
    op.add_column("alvos", sa.Column("detector", sa.String(10), nullable=False, server_default="ewma"))
    op.create_check_constraint("ck_alvos_interval", "alvos", "intervalo_s BETWEEN 0.1 AND 3600")
    op.create_check_constraint("ck_alvos_timeout", "alvos", "timeout_s BETWEEN 0.05 AND 10")
    op.create_check_constraint("ck_alvos_detector", "alvos", "detector IN ('ewma','mad')")


def downgrade():
    op.drop_index("ix_eventos_incidentes_id", table_name="eventos_operacionais")
    for name in ("ck_alvos_detector", "ck_alvos_timeout", "ck_alvos_interval"):
        op.drop_constraint(name, "alvos", type_="check")
    for name in ("detector", "timeout_s", "intervalo_s"):
        op.drop_column("alvos", name)
