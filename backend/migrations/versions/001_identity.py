"""Identidades persistentes e sessões revogáveis."""
from alembic import op
import sqlalchemy as sa

revision = "001_identity"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("usuarios",
        sa.Column("username", sa.String(100), primary_key=True),
        sa.Column("senha_hash", sa.String(512), nullable=False),
        sa.Column("papel", sa.String(32), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("versao", sa.Integer(), nullable=False),
        sa.CheckConstraint("papel IN ('suporte_n1','analista_redes','gestor_ti')"))
    op.create_table("sessoes",
        sa.Column("jti", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(100), sa.ForeignKey("usuarios.username"), nullable=False),
        sa.Column("papel", sa.String(32), nullable=False),
        sa.Column("versao_usuario", sa.Integer(), nullable=False),
        sa.Column("emitida_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revogada", sa.Boolean(), nullable=False))
    op.create_index("ix_sessoes_username", "sessoes", ["username"])
    op.create_index("ix_sessoes_expira_em", "sessoes", ["expira_em"])


def downgrade():
    op.drop_table("sessoes")
    op.drop_table("usuarios")
