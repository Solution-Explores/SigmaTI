"""Repositório PostgreSQL: alterações de estado e eventos confirmam juntos."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import math
import json
import re
import uuid

from sqlalchemy import delete, select, text, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from sigma_eng.state import StateConflict, detector_snapshot, restore_detector
from sigma_eng.anomaly import EwmaDetector, MadDetector
from .database import PersistenceUnavailable
from .operational_models import (AggregateRow, ApprovalRow, DetectorRow, EventRow,
                                 ExecutionRow, IncidentRow, MeasurementRow, SloRow, TargetRow)

STATE_TABLES = {"approvals": ApprovalRow, "executions": ExecutionRow, "detectors": DetectorRow}

# Templates estáveis no caminho quente: sem recompilar três INSERTs por amostra.
MEASUREMENT_INSERT = text("INSERT INTO medicoes (id, ts, alvo_id, sucesso, latencia_ms) "
    "VALUES (:id, :ts, :target, :success, :latency) "
    "ON CONFLICT (id, ts) DO NOTHING RETURNING id")
AGGREGATE_UPSERT = text("INSERT INTO medicoes_agregadas "
    "(alvo_id, periodo, ts, total, sucessos, latencia_n, latencia_soma, latencia_min, latencia_max) VALUES "
    "(:target, 'minute', :minute, 1, :successes, :n, :sum, :latency, :latency), "
    "(:target, 'hour', :hour, 1, :successes, :n, :sum, :latency, :latency) "
    "ON CONFLICT (alvo_id, periodo, ts) DO UPDATE SET "
    "total=medicoes_agregadas.total+EXCLUDED.total, "
    "sucessos=medicoes_agregadas.sucessos+EXCLUDED.sucessos, "
    "latencia_n=medicoes_agregadas.latencia_n+EXCLUDED.latencia_n, "
    "latencia_soma=medicoes_agregadas.latencia_soma+EXCLUDED.latencia_soma, "
    "latencia_min=LEAST(medicoes_agregadas.latencia_min,EXCLUDED.latencia_min), "
    "latencia_max=GREATEST(medicoes_agregadas.latencia_max,EXCLUDED.latencia_max)")



def utc(value=None):
    value = value or datetime.now(timezone.utc)
    if value.tzinfo is None:
        raise ValueError("timestamp deve conter fuso horário")
    return value.astimezone(timezone.utc)


def columns(row):
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


class PostgresOperationalStore:
    def __init__(self, engine):
        self.engine = engine

    @contextmanager
    def transaction(self):
        try:
            with Session(self.engine) as session, session.begin():
                yield session
        except SQLAlchemyError:
            raise PersistenceUnavailable("Operação de persistência indisponível.") from None

    def _event(self, session, actor, action, resource, details=None):
        # Serializa a atribuição dos IDs até o commit: futura leitura incremental
        # não pode ultrapassar um evento anterior ainda não confirmado.
        # Flush dos dados antes do lock global e apenas uma ida para lock+evento.
        # O lock permanece até o commit, preservando ordem de replay entre workers.
        session.flush()
        session.execute(text("WITH event_lock AS MATERIALIZED "
            "(SELECT pg_advisory_xact_lock(7417001)) "
            "INSERT INTO eventos_operacionais (ts, ator, acao, recurso, detalhes) "
            "SELECT :ts, :actor, :action, :resource, CAST(:details AS JSONB) FROM event_lock"),
            {"ts": utc(), "actor": actor, "action": action, "resource": resource,
             "details": json.dumps(details or {}, allow_nan=False)})

    def create(self, kind, identifier, data):
        model = STATE_TABLES[kind]
        value = dict(data, versao=1)
        with self.transaction() as session:
            result = session.execute(insert(model).values(id=identifier, documento=value, versao=1,
                estado=value.get("estado", value.get("status", "ready")), atualizado_em=utc())
                .on_conflict_do_nothing(index_elements=["id"]).returning(model.id)).scalar_one_or_none()
            if result is None:
                raise StateConflict("identificador existente")
            self._event(session, value.get("solicitante", "system"), f"{kind}.created", identifier)
        return value

    def get(self, kind, identifier):
        with self.transaction() as session:
            row = session.get(STATE_TABLES[kind], identifier)
            if row is None:
                raise KeyError(identifier)
            return dict(row.documento, versao=row.versao)

    def save(self, kind, identifier, data, version):
        model = STATE_TABLES[kind]
        value = dict(data, versao=version + 1)
        with self.transaction() as session:
            changed = session.execute(update(model).where(model.id == identifier, model.versao == version)
                .values(documento=value, versao=version + 1,
                        estado=value.get("estado", value.get("status", "ready")), atualizado_em=utc()))
            if changed.rowcount != 1:
                raise StateConflict("estado alterado; recarregue antes de decidir")
            self._event(session, value.get("decidida_por") or "system", f"{kind}.updated", identifier,
                        {"versao": version + 1, "estado": value.get("estado", value.get("status", "ready"))})
        return value

    def list(self, kind):
        with self.transaction() as session:
            return [dict(row.documento, versao=row.versao) for row in session.scalars(select(STATE_TABLES[kind]))]

    def create_target(self, nome, host, porta, kind="tcp", actor="system",
                      intervalo_s=1.0, timeout_s=1.0, detector="ewma"):
        if not 1 <= len(nome) <= 100 or not 1 <= len(host) <= 253 or not 1 <= porta <= 65535:
            raise ValueError("alvo inválido")
        if kind not in ("tcp", "http", "https"):
            raise ValueError("tipo de sonda inválido")
        if (not math.isfinite(intervalo_s) or not 0.1 <= intervalo_s <= 3600
                or not math.isfinite(timeout_s) or not 0.05 <= timeout_s <= 10
                or detector not in ("ewma", "mad")):
            raise ValueError("configuração de coleta inválida")
        with self.transaction() as session:
            row = TargetRow(id=str(uuid.uuid4()), nome=nome, host=host, porta=porta,
                            kind=kind, ativo=True, criado_em=utc(),
                            intervalo_s=intervalo_s, timeout_s=timeout_s, detector=detector)
            session.add(row)
            session.flush()
            self._event(session, actor, "target.created", row.id)
            return columns(row)

    def list_targets(self, limit=500):
        with self.transaction() as session:
            return [columns(row) for row in session.scalars(select(TargetRow).order_by(TargetRow.criado_em)
                                                           .limit(min(limit, 500)))]

    def collection_targets(self):
        with self.transaction() as session:
            # Não truncar silenciosamente a lista pública de 500 alvos.
            return [columns(row) for row in session.scalars(
                select(TargetRow).where(TargetRow.ativo.is_(True)).order_by(TargetRow.id))]

    def configure_target(self, identifier, active, actor):
        with self.transaction() as session:
            row = session.scalar(select(TargetRow).where(TargetRow.id == identifier).with_for_update())
            if row is None:
                raise KeyError(identifier)
            row.ativo = active
            self._event(session, actor, "target.configured", identifier, {"ativo": active})
            return columns(row)

    def _partition(self, session, ts):
        start = ts.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        name = f"medicoes_{start:%Y%m}"
        if session.scalar(text("SELECT to_regclass(:name)"), {"name": name}) is None:
            session.execute(text("SELECT pg_advisory_xact_lock(7417002)"))
            # Nome e limites derivados exclusivamente de datetime, nunca de SQL do cliente.
            session.execute(text(f"CREATE TABLE IF NOT EXISTS {name} PARTITION OF medicoes "
                                 f"FOR VALUES FROM ('{start.isoformat()}') TO ('{end.isoformat()}')"))

    def _aggregate(self, session, target_id, ts, success, latency):
        minute = ts.replace(second=0, microsecond=0)
        session.execute(AGGREGATE_UPSERT, {"target":target_id, "minute":minute,
            "hour":minute.replace(minute=0), "successes":int(success),
            "n":int(latency is not None), "sum":latency or 0, "latency":latency})

    def _incident(self, session, target_id, ts, kind="availability"):
        identifier = str(uuid.uuid4())
        created = session.execute(insert(IncidentRow).values(id=identifier, alvo_id=target_id,
            tipo=kind, severidade="P3", detectado_em=ts)
            .on_conflict_do_nothing(index_elements=["alvo_id", "tipo"],
                                   index_where=IncidentRow.resolvido_em.is_(None))
            .returning(IncidentRow.id)).scalar_one_or_none()
        row = session.scalar(select(IncidentRow).where(IncidentRow.alvo_id == target_id,
                                                      IncidentRow.tipo == kind, IncidentRow.resolvido_em.is_(None)))
        return columns(row), created is not None

    def record_measurement(self, target_id, success, latency_ms=None, ts=None, identifier=None, *, detector_kind=None):
        ts = utc(ts)
        if type(success) is not bool or (latency_ms is not None and
                (not math.isfinite(latency_ms) or latency_ms < 0)):
            raise ValueError("medição inválida")
        if detector_kind not in (None, "ewma", "mad"):
            raise ValueError("detector inválido")
        identifier = str(uuid.UUID(identifier)) if identifier else str(uuid.uuid4())
        with self.transaction() as session:
            self._partition(session, ts)
            target = session.scalar(select(TargetRow).where(TargetRow.id == target_id).with_for_update())
            if target is None:
                raise KeyError(target_id)
            inserted = session.execute(MEASUREMENT_INSERT, {"id":identifier, "ts":ts,
                "target":target_id, "success":success, "latency":latency_ms}).scalar_one_or_none()
            if inserted is None:
                previous = session.get(MeasurementRow, (identifier, ts))
                if (previous.alvo_id != target_id or previous.sucesso != success
                        or previous.latencia_ms != latency_ms):
                    raise StateConflict("identificador de medição reutilizado com outros dados")
                active = session.scalar(select(IncidentRow).where(IncidentRow.alvo_id == target_id,
                    IncidentRow.tipo == "availability", IncidentRow.resolvido_em.is_(None))) if not success else None
                return {"inserted": False, "incident": columns(active) if active else None}
            anomaly = False
            if detector_kind is not None:
                stored = session.get(DetectorRow, target_id)
                detector = (restore_detector(stored.documento) if stored is not None
                    and stored.documento["kind"] == detector_kind else
                    EwmaDetector() if detector_kind == "ewma" else MadDetector())
                if success and latency_ms is not None:
                    anomaly = detector.update(latency_ms)
                version = stored.versao + 1 if stored is not None else 1
                data = dict(detector_snapshot(detector), versao=version)
                if stored is None:
                    session.add(DetectorRow(id=target_id, documento=data, versao=version,
                                            estado="ready", atualizado_em=ts))
                else:
                    stored.documento, stored.versao, stored.atualizado_em = data, version, ts
            self._aggregate(session, target_id, ts, success, latency_ms)
            incident, created = self._incident(session, target_id, ts) if not success else (None, False)
            # Telemetria contínua já tem registro imutável em medicoes. Não
            # serializar todas as amostras no cursor global dos eventos de domínio.
            # Incidentes e ações administrativas continuam auditados na transação.
            if detector_kind is None:
                self._event(session, "scheduler", "measurement.recorded", target_id, {"sucesso": success})
            if created:
                self._event(session, "scheduler", "incident.created", incident["id"], {"alvo_id": target_id})
            latency_incident = None
            if anomaly:
                latency_incident, latency_created = self._incident(session, target_id, ts, "latency")
                if latency_created:
                    self._event(session, "scheduler", "incident.created", latency_incident["id"],
                                {"alvo_id": target_id, "tipo": "latency"})
            return {"inserted": True, "incident": incident or latency_incident}

    def measurements(self, target_id, limit=1000):
        with self.transaction() as session:
            return [columns(row) for row in session.scalars(select(MeasurementRow)
                .where(MeasurementRow.alvo_id == target_id).order_by(MeasurementRow.ts.desc()).limit(min(limit, 1000)))]

    def aggregates(self, target_id, period, limit=1000):
        if period not in ("minute", "hour"):
            raise ValueError("período inválido")
        with self.transaction() as session:
            rows = session.scalars(select(AggregateRow).where(AggregateRow.alvo_id == target_id,
                AggregateRow.periodo == period).order_by(AggregateRow.ts.desc()).limit(min(limit, 1000)))
            return [dict(columns(row), latencia_media=row.latencia_soma / row.latencia_n if row.latencia_n else None)
                    for row in rows]

    def incidents(self, active_only=False, limit=500):
        query = select(IncidentRow)
        if active_only:
            query = query.where(IncidentRow.resolvido_em.is_(None))
        with self.transaction() as session:
            return [columns(row) for row in session.scalars(query.order_by(IncidentRow.detectado_em.desc())
                                                           .limit(min(limit, 500)))]

    def change_incident(self, identifier, action, actor):
        if action not in ("ack", "resolve"):
            raise ValueError("transição inválida")
        with self.transaction() as session:
            target_id = session.scalar(select(IncidentRow.alvo_id).where(IncidentRow.id == identifier))
            if target_id is None:
                raise KeyError(identifier)
            # Mesma ordem de locks da ingestão: alvo antes de incidente.
            session.scalar(select(TargetRow.id).where(TargetRow.id == target_id).with_for_update())
            row = session.scalar(select(IncidentRow).where(IncidentRow.id == identifier).with_for_update())
            field = "reconhecido_em" if action == "ack" else "resolvido_em"
            if row.resolvido_em is None and getattr(row, field) is None:
                setattr(row, field, max(utc(), row.detectado_em))
                self._event(session, actor, f"incident.{action}", identifier)
            return columns(row)

    def save_slo(self, target_id, percentage, days, actor):
        if not 0 < percentage < 100 or not 1 <= days <= 3650:
            raise ValueError("SLO inválido")
        with self.transaction() as session:
            if session.get(TargetRow, target_id) is None:
                raise KeyError(target_id)
            session.execute(insert(SloRow).values(alvo_id=target_id, alvo_pct=percentage, janela_dias=days)
                .on_conflict_do_update(index_elements=["alvo_id"], set_={"alvo_pct": percentage, "janela_dias": days}))
            self._event(session, actor, "slo.updated", target_id)

    def get_slo(self, target_id):
        with self.transaction() as session:
            row = session.get(SloRow, target_id)
            return columns(row) if row is not None else None

    def events(self, after=0, limit=500):
        with self.transaction() as session:
            return [columns(row) for row in session.scalars(select(EventRow).where(EventRow.id > after)
                                                           .order_by(EventRow.id).limit(min(limit, 500)))]

    def stream_events(self, after=0, limit=100):
        with self.transaction() as session:
            rows = session.scalars(select(EventRow).where(EventRow.id > after,
                text("acao IN ('incident.created','incident.ack','incident.resolve')"))
                .order_by(EventRow.id).limit(min(limit, 100)))
            # Projeção explícita: sem ator, texto livre ou eventos de aprovação/execução.
            return [{"id": row.id, "ts": row.ts.isoformat(), "acao": row.acao,
                     "incidente_id": row.recurso,
                     "alvo_id": row.detalhes.get("alvo_id")} for row in rows]

    def retain(self, days, now=None):
        if type(days) is not int or not 1 <= days <= 3650:
            raise ValueError("retenção deve estar entre 1 e 3650 dias")
        cutoff = utc(now) - timedelta(days=days)
        with self.transaction() as session:
            session.execute(text("SELECT pg_advisory_xact_lock(7417002)"))
            deleted = session.execute(delete(MeasurementRow).where(MeasurementRow.ts < cutoff)).rowcount
            # Agregados permanecem; remover a partição só quando o mês inteiro venceu.
            names = session.scalars(text("SELECT c.relname FROM pg_inherits i JOIN pg_class c ON c.oid=i.inhrelid "
                                         "WHERE i.inhparent='medicoes'::regclass")).all()
            dropped = []
            for name in names:
                if re.fullmatch(r"medicoes_\d{6}", name):
                    start = datetime.strptime(name[-6:], "%Y%m").replace(tzinfo=timezone.utc)
                    end = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
                    if end <= cutoff:
                        session.execute(text(f"DROP TABLE {name}"))
                        dropped.append(name)
            self._event(session, "maintenance", "measurements.retained", "medicoes", {"dias": days, "removidas": deleted})
            return {"removidas": deleted, "particoes": dropped}
