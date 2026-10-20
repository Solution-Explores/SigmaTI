"""Esquema inicial de identidades e sessões (UTC, sem tokens em claro)."""
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "usuarios"
    __table_args__ = (CheckConstraint("papel IN ('suporte_n1','analista_redes','gestor_ti')"),)
    username: Mapped[str] = mapped_column(String(100), primary_key=True)
    senha_hash: Mapped[str] = mapped_column(String(512))
    papel: Mapped[str] = mapped_column(String(32))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    versao: Mapped[int] = mapped_column(Integer, default=1)


class SessionRow(Base):
    __tablename__ = "sessoes"
    jti: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(ForeignKey("usuarios.username"), index=True)
    papel: Mapped[str] = mapped_column(String(32))
    versao_usuario: Mapped[int] = mapped_column(Integer)
    emitida_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revogada: Mapped[bool] = mapped_column(Boolean, default=False)
