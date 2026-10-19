"""Roteador FastAPI com o núcleo de engenharia.

Integração no ``main.py`` do SIGMA::

    from sigma_eng.api import create_router
    app.include_router(create_router(exige_papel))

Variáveis de ambiente:
  SIGMA_AUDIT_PATH   arquivo JSONL da trilha (padrão: resultados/audit.jsonl, relativo à aplicação)
  SIGMA_AUDIT_KEY    chave HMAC da trilha (recomendado em produção)
  SIGMA_PROBE_NETS   redes alvo permitidas, separadas por vírgula (padrão: RFC 1918 + loopback)
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from . import anomaly, incidents, probe, slo
from .audit_chain import AuditChain


def _redes() -> list[str]:
    env = os.getenv("SIGMA_PROBE_NETS")
    return [n.strip() for n in env.split(",") if n.strip()] if env else list(probe.DEFAULT_ALLOWED_NETWORKS)


class ProbeIn(BaseModel):
    host: str = Field(min_length=1, max_length=253)
    port: int = Field(ge=1, le=65535)
    kind: str = "tcp"
    count: int = Field(default=1, ge=1, le=100)


class IntervaloIn(BaseModel):
    inicio: datetime
    fim: datetime


class SloIn(BaseModel):
    alvo_pct: float = 99.9
    janela_dias: int = 30
    indisponibilidades: list[IntervaloIn]
    agora: datetime | None = None


class IncidenteIn(BaseModel):
    id: str
    severidade: str = "P3"
    inicio_real: datetime | None = None
    detectado_em: datetime | None = None
    reconhecido_em: datetime | None = None
    resolvido_em: datetime | None = None


class AnomaliaIn(BaseModel):
    serie: list[float] = Field(min_length=2, max_length=100_000)
    metodo: str = "ewma"


def create_router(
    exige_papel: Callable[[str], Callable], *, auditoria: AuditChain | None = None,
) -> APIRouter:
    """Cria rotas protegidas com a política RBAC fornecida pela aplicação.

    A dependência de autenticação é obrigatória: não há roteador global nem
    fallback que permita executar operações sem a política da aplicação.
    Importar este módulo não abre arquivos nem depende de módulos da aplicação.
    """
    if not callable(exige_papel):
        raise TypeError("Forneça a política de autorização da aplicação.")
    if auditoria is None:
        key = os.getenv("SIGMA_AUDIT_KEY")
        auditoria = AuditChain(os.getenv("SIGMA_AUDIT_PATH", "resultados/audit.jsonl"),
                               chave=key.encode() if key else None)
    router = APIRouter(prefix="/api/eng", tags=["engenharia"])

    @router.post("/probe", dependencies=[Depends(exige_papel("analista_redes"))])
    async def post_probe(body: ProbeIn) -> dict:
        if body.kind not in probe.VALID_KINDS:
            raise HTTPException(422, f"kind deve ser um de {sorted(probe.VALID_KINDS)}")
        if not await asyncio.to_thread(probe.is_target_allowed, body.host, _redes()):
            raise HTTPException(403, "alvo fora das redes autorizadas")
        stats = await asyncio.to_thread(probe.probe_many, body.host, body.port, body.kind, body.count)
        auditoria.registrar("api", "probe.executed", f"{body.host}:{body.port}", {"kind": body.kind, "count": body.count})
        return stats.as_dict()

    @router.post("/slo/avaliar", dependencies=[Depends(exige_papel("analista_redes"))])
    def post_slo(body: SloIn) -> dict:
        try:
            objetivo = slo.SLO("api", body.alvo_pct, body.janela_dias)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        agora = body.agora or datetime.now(timezone.utc)
        ivs = [(i.inicio, i.fim) for i in body.indisponibilidades]
        return {"orcamento": slo.error_budget(objetivo, ivs, agora).as_dict(), "alertas": slo.burn_alerts(objetivo, ivs, agora)}

    @router.post("/incidentes/metricas", dependencies=[Depends(exige_papel("analista_redes"))])
    def post_metricas(body: list[IncidenteIn]) -> dict:
        return incidents.metricas(incidents.Incidente(**i.model_dump()) for i in body)

    @router.post("/anomalias", dependencies=[Depends(exige_papel("analista_redes"))])
    def post_anomalias(body: AnomaliaIn) -> dict:
        if body.metodo == "ewma":
            det: anomaly.Detector = anomaly.EwmaDetector()
        elif body.metodo == "mad":
            det = anomaly.MadDetector()
        else:
            raise HTTPException(422, "metodo deve ser 'ewma' ou 'mad'")
        return {"indices": [i for i, x in enumerate(body.serie) if det.update(x)]}

    @router.get("/auditoria/verificar", dependencies=[Depends(exige_papel("gestor_ti"))])
    def get_verificar() -> dict:
        ok, indice = auditoria.verificar()
        return {"integra": ok, "primeira_invalida": indice, "entradas": len(auditoria)}

    return router
