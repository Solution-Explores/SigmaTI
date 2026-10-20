"""Dados operacionais, séries particionadas e eventos transacionais."""
from datetime import datetime

from sqlalchemy import (BigInteger, Boolean, CheckConstraint, DateTime, Float,
                        ForeignKey, Index, Integer, String, text)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .models import Base


class TargetRow(Base):
    __tablename__ = "alvos"
    __table_args__ = (CheckConstraint("porta BETWEEN 1 AND 65535"),
                     CheckConstraint("kind IN ('tcp','http','https')"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    host: Mapped[str] = mapped_column(String(253))
    porta: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(10), default="tcp")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MeasurementRow(Base):
    __tablename__ = "medicoes"
    __table_args__ = (Index("ix_medicoes_alvo_ts", "alvo_id", "ts"),
                     CheckConstraint("latencia_ms IS NULL OR latencia_ms >= 0"),
                     {"postgresql_partition_by": "RANGE (ts)"})
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    alvo_id: Mapped[str] = mapped_column(ForeignKey("alvos.id"))
    sucesso: Mapped[bool] = mapped_column(Boolean)
    latencia_ms: Mapped[float | None] = mapped_column(Float)


class AggregateRow(Base):
    __tablename__ = "medicoes_agregadas"
    __table_args__ = (CheckConstraint("periodo IN ('minute','hour')"),)
    alvo_id: Mapped[str] = mapped_column(ForeignKey("alvos.id"), primary_key=True)
    periodo: Mapped[str] = mapped_column(String(10), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    total: Mapped[int] = mapped_column(BigInteger)
    sucessos: Mapped[int] = mapped_column(BigInteger)
    latencia_n: Mapped[int] = mapped_column(BigInteger)
    latencia_soma: Mapped[float] = mapped_column(Float)
    latencia_min: Mapped[float | None] = mapped_column(Float)
    latencia_max: Mapped[float | None] = mapped_column(Float)


class IncidentRow(Base):
    __tablename__ = "incidentes"
    __table_args__ = (Index("uq_incidente_ativo", "alvo_id", "tipo", unique=True,
                           postgresql_where=text("resolvido_em IS NULL")),
                     CheckConstraint("severidade IN ('P1','P2','P3')"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    alvo_id: Mapped[str] = mapped_column(ForeignKey("alvos.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(40))
    severidade: Mapped[str] = mapped_column(String(2), default="P3")
    detectado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reconhecido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolvido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class StateMixin:
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    documento: Mapped[dict] = mapped_column(JSONB)
    versao: Mapped[int] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(32), index=True)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ApprovalRow(StateMixin, Base):
    __tablename__ = "aprovacoes"


class ExecutionRow(StateMixin, Base):
    __tablename__ = "execucoes_runbook"


class DetectorRow(StateMixin, Base):
    __tablename__ = "detectores"


class SloRow(Base):
    __tablename__ = "slo"
    __table_args__ = (CheckConstraint("alvo_pct > 0 AND alvo_pct < 100"),
                     CheckConstraint("janela_dias > 0"))
    alvo_id: Mapped[str] = mapped_column(ForeignKey("alvos.id"), primary_key=True)
    alvo_pct: Mapped[float] = mapped_column(Float)
    janela_dias: Mapped[int] = mapped_column(Integer)


class EventRow(Base):
    __tablename__ = "eventos_operacionais"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ator: Mapped[str] = mapped_column(String(100))
    acao: Mapped[str] = mapped_column(String(80))
    recurso: Mapped[str] = mapped_column(String(100))
    detalhes: Mapped[dict] = mapped_column(JSONB)
