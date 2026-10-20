"""Contratos e snapshots puros; nenhum banco/framework é importado pelo núcleo."""
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime
import json
import math
import threading
from typing import Protocol


class StateConflict(ValueError):
    """Identificador existente ou revisão alterada por outro operador/worker."""


class StateRepository(Protocol):
    def create(self, kind: str, identifier: str, data: dict) -> dict: ...
    def get(self, kind: str, identifier: str) -> dict: ...
    def save(self, kind: str, identifier: str, data: dict, version: int) -> dict: ...
    def list(self, kind: str) -> list[dict]: ...


class MonitoringRepository(Protocol):
    def create_target(self, nome: str, host: str, porta: int, kind: str = "tcp", actor: str = "system",
                      intervalo_s: float = 1.0, timeout_s: float = 1.0, detector: str = "ewma") -> dict: ...
    def list_targets(self, limit: int = 500) -> list[dict]: ...
    def record_measurement(self, target_id: str, success: bool, latency_ms: float | None = None,
                           ts: datetime | None = None, identifier: str | None = None, *, detector_kind: str | None = None) -> dict: ...
    def collection_targets(self) -> list[dict]: ...
    def configure_target(self, identifier: str, active: bool, actor: str) -> dict: ...
    def stream_events(self, after: int = 0, limit: int = 100) -> list[dict]: ...
    def measurements(self, target_id: str, limit: int = 1000) -> list[dict]: ...
    def aggregates(self, target_id: str, period: str, limit: int = 1000) -> list[dict]: ...
    def incidents(self, active_only: bool = False, limit: int = 500) -> list[dict]: ...
    def change_incident(self, identifier: str, action: str, actor: str) -> dict: ...
    def save_slo(self, target_id: str, percentage: float, days: int, actor: str) -> None: ...
    def get_slo(self, target_id: str) -> dict | None: ...
    def events(self, after: int = 0, limit: int = 500) -> list[dict]: ...
    def retain(self, days: int, now: datetime | None = None) -> dict: ...


class OperationalRepository(StateRepository, MonitoringRepository, Protocol):
    pass


def snapshot(value) -> dict:
    def encode(item):
        if isinstance(item, datetime):
            if item.tzinfo is None:
                raise ValueError("timestamp deve conter fuso horário")
            return item.isoformat()
        raise TypeError(type(item).__name__)
    return json.loads(json.dumps(asdict(value), default=encode, allow_nan=False))


class MemoryStateRepository:
    """Implementação para testes com cópia defensiva e CAS igual ao PostgreSQL."""
    def __init__(self):
        self._items = {}
        self._lock = threading.Lock()

    def create(self, kind, identifier, data):
        with self._lock:
            if (kind, identifier) in self._items:
                raise StateConflict("identificador existente")
            value = deepcopy(dict(data, versao=1))
            self._items[kind, identifier] = value
            return deepcopy(value)

    def get(self, kind, identifier):
        with self._lock:
            return deepcopy(self._items[kind, identifier])

    def save(self, kind, identifier, data, version):
        with self._lock:
            if self._items[kind, identifier]["versao"] != version:
                raise StateConflict("estado alterado; recarregue antes de decidir")
            value = deepcopy(dict(data, versao=version + 1))
            self._items[kind, identifier] = value
            return deepcopy(value)

    def list(self, kind):
        with self._lock:
            return deepcopy([value for (item_kind, _), value in self._items.items() if item_kind == kind])


def detector_snapshot(detector) -> dict:
    from .anomaly import EwmaDetector, MadDetector
    if isinstance(detector, EwmaDetector):
        return {"kind": "ewma", "config": {"alpha": detector.alpha, "k": detector.k,
            "aquecimento": detector.aquecimento, "piso_desvio": detector.piso,
            "congelar_em_anomalia": detector.congelar, "reaprender_apos": detector.reaprender_apos},
            "state": {"n": detector.n, "media": detector.media, "var": detector.var,
                      "seguidas": detector._seguidas}, "versao": 1}
    if isinstance(detector, MadDetector):
        return {"kind": "mad", "config": {"janela": detector.buf.maxlen, "k": detector.k,
            "aquecimento": detector.aquecimento, "piso_escala": detector.piso},
            "state": {"buf": list(detector.buf)}, "versao": 1}
    raise ValueError("detector não suportado")


def restore_detector(data):
    from .anomaly import EwmaDetector, MadDetector
    if data["kind"] == "ewma":
        det = EwmaDetector(**data["config"])
        state = data["state"]
        if (type(state["n"]) is not int or state["n"] < 0
                or type(state["seguidas"]) is not int or state["seguidas"] < 0
                or not all(math.isfinite(state[k]) for k in ("media", "var")) or state["var"] < 0):
            raise ValueError("estado EWMA inválido")
        det.n, det.media, det.var, det._seguidas = (state[k] for k in ("n", "media", "var", "seguidas"))
        return det
    if data["kind"] == "mad":
        det = MadDetector(**data["config"])
        values = data["state"]["buf"]
        if len(values) > det.buf.maxlen or not all(math.isfinite(v) for v in values):
            raise ValueError("estado MAD inválido")
        det.buf.extend(values)
        return det
    raise ValueError("detector não suportado")
