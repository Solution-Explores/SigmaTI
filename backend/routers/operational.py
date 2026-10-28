"""Operações persistentes protegidas. Não inicia sondas, scheduler ou comandos."""
from contextlib import contextmanager
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from pydantic import BaseModel, Field

from auth import Usuario, exige_papel
from sigma_eng.approvals import ApprovalService, AprovacaoError
from sigma_eng.state import StateConflict, OperationalRepository

router = APIRouter(prefix="/api/eng", tags=["operacao-persistente"])
Reader = Annotated[Usuario, Depends(exige_papel("suporte_n1"))]
Analyst = Annotated[Usuario, Depends(exige_papel("analista_redes"))]
Manager = Annotated[Usuario, Depends(exige_papel("gestor_ti"))]
Identifier = Annotated[str, Path(min_length=1, max_length=100)]


def repository(request: Request) -> OperationalRepository:
    store = request.app.state.operational_store
    if store is None:
        raise HTTPException(503, "Persistência operacional não configurada.")
    return store


@contextmanager
def errors():
    try:
        yield
    except KeyError:
        raise HTTPException(404, "Registro inexistente.") from None
    except (StateConflict, AprovacaoError):
        raise HTTPException(409, "Operação incompatível com o estado atual.") from None
    except ValueError:
        raise HTTPException(422, "Dados inválidos.") from None


class TargetIn(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    host: str = Field(min_length=1, max_length=253)
    porta: int = Field(ge=1, le=65535)
    kind: Literal["tcp", "http", "https"] = "tcp"
    intervalo_s: float = Field(default=1.0, ge=0.1, le=3600, allow_inf_nan=False)
    timeout_s: float = Field(default=1.0, ge=0.05, le=10, allow_inf_nan=False)
    detector: Literal["ewma", "mad"] = "ewma"


class ApprovalIn(BaseModel):
    acao: str = Field(min_length=1, max_length=200)
    papel_minimo: Literal["analista_redes", "gestor_ti"] = "analista_redes"


class DecisionIn(BaseModel):
    aprovar: bool
    justificativa: str | None = Field(default=None, max_length=500)


class SloIn(BaseModel):
    alvo_pct: float = Field(gt=0, lt=100)
    janela_dias: int = Field(ge=1, le=3650)


@router.post("/alvos")
def create_target(body: TargetIn, request: Request, user: Analyst):
    with errors():
        return repository(request).create_target(**body.model_dump(), actor=user.username)


class TargetActiveIn(BaseModel):
    ativo: bool


@router.patch("/alvos/{identifier}")
def configure_target(identifier: Identifier, body: TargetActiveIn, request: Request, user: Analyst):
    with errors():
        return repository(request).configure_target(identifier, body.ativo, user.username)


@router.get("/coleta/status")
def collection_status(request: Request, user: Analyst):
    scheduler = getattr(request.app.state, "scheduler", None)
    return {"habilitada": scheduler is not None,
            "metricas": scheduler.status() if scheduler is not None else {}}


@router.get("/alvos")
def list_targets(request: Request, user: Reader, limit: int = Query(100, ge=1, le=500)):
    return {"alvos": repository(request).list_targets(limit)}


@router.get("/alvos/{identifier}/medicoes")
def measurements(identifier: Identifier, request: Request, user: Reader,
                 limit: int = Query(100, ge=1, le=1000)):
    return {"medicoes": repository(request).measurements(identifier, limit)}


@router.get("/alvos/{identifier}/agregados")
def aggregates(identifier: Identifier, request: Request, user: Reader,
               periodo: Literal["minute", "hour"] = "minute", limit: int = Query(100, ge=1, le=1000)):
    return {"agregados": repository(request).aggregates(identifier, periodo, limit)}


@router.get("/incidentes")
def incidents(request: Request, user: Reader, ativos: bool = False):
    return {"incidentes": repository(request).incidents(ativos)}


@router.post("/incidentes/{identifier}/reconhecer")
def acknowledge(identifier: Identifier, request: Request, user: Analyst):
    with errors():
        return repository(request).change_incident(identifier, "ack", user.username)


@router.post("/incidentes/{identifier}/resolver")
def resolve(identifier: Identifier, request: Request, user: Analyst):
    with errors():
        return repository(request).change_incident(identifier, "resolve", user.username)


@router.post("/aprovacoes")
def request_approval(body: ApprovalIn, request: Request, user: Analyst):
    with errors():
        return ApprovalService(repository=repository(request)).solicitar(
            body.acao, user.username, body.papel_minimo)


@router.get("/aprovacoes")
def pending_approvals(request: Request, user: Analyst):
    with errors():
        return {"aprovacoes": ApprovalService(repository=repository(request)).pendentes()}


@router.post("/aprovacoes/{identifier}/decidir")
def decide(identifier: Identifier, body: DecisionIn, request: Request, user: Analyst):
    with errors():
        service = ApprovalService(repository=repository(request))
        method = service.aprovar if body.aprovar else service.rejeitar
        return method(identifier, user.username, user.papel, body.justificativa)


@router.get("/execucoes/{identifier}")
def execution(identifier: Identifier, request: Request, user: Analyst):
    with errors():
        data = repository(request).get("executions", identifier)
        # O estado operacional não precisa expor comandos, variáveis ou saída bruta.
        return {**{key: data[key] for key in ("id", "status", "aguardando", "versao", "passo_em_execucao")},
                "resultados": [{key: item[key] for key in ("passo_id", "ok", "codigo", "simulado")}
                               for item in data["resultados"]]}


@router.post("/alvos/{identifier}/slo")
def save_slo(identifier: Identifier, body: SloIn, request: Request, user: Analyst):
    with errors():
        repository(request).save_slo(identifier, body.alvo_pct, body.janela_dias, user.username)
        return {"status": "salvo"}


@router.get("/alvos/{identifier}/slo")
def slo(identifier: Identifier, request: Request, user: Reader):
    result = repository(request).get_slo(identifier)
    if result is None:
        raise HTTPException(404, "SLO não cadastrado.")
    return result


@router.get("/auditoria/eventos")
def events(request: Request, user: Manager, after: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    return {"eventos": repository(request).events(after, limit)}


@router.get("/saude")
def health(request: Request, user: Reader, limit: int = Query(500,ge=1,le=500)):
    return repository(request).health_snapshot(limit)


@router.get("/incidentes/resumo")
def incident_summary(request: Request, user: Analyst):
    from sigma_eng.incidents import Incidente, metricas
    store=repository(request)
    rows=store.incidents(limit=500)
    names={target["id"]:target["nome"] for target in store.list_targets(500)}
    values=[Incidente(id=row["id"],severidade=row["severidade"],detectado_em=row["detectado_em"],
        reconhecido_em=row["reconhecido_em"],resolvido_em=row["resolvido_em"]) for row in rows]
    return {"incidentes":[dict(row,nome_alvo=names.get(row["alvo_id"])) for row in rows],
            "metricas":metricas(values),"limite":500}


@router.get("/aprovacoes/{identifier}")
def approval_detail(identifier: Identifier, request: Request, user: Analyst):
    with errors():
        store=repository(request)
        store.get("approvals",identifier)
        return ApprovalService(repository=store).obter(identifier)


@router.get("/auditoria/recentes")
def recent_events(request: Request, user: Manager):
    return {"eventos":repository(request).recent_events(100)}
