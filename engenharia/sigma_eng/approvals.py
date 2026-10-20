"""Aprovação humana com máquina de estados, TTL e separação de funções.

Aprovação de ações sensíveis. Características:
  * transições explícitas e validadas (pending → approved | rejected | expired);
  * **quatro olhos**: quem solicita não aprova a própria solicitação;
  * papel mínimo para decidir (perfis do SIGMA: N1 < Analista < Gestor);
  * expiração avaliada na decisão, não só por varredura periódica (uma
    solicitação vencida nunca pode ser aprovada entre duas varreduras).
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable

from .audit_chain import AuditChain
from .state import StateConflict, StateRepository, snapshot

PAPEIS = {"suporte_n1": 1, "analista_redes": 2, "gestor_ti": 3}

TRANSICOES = {
    "pending": {"approved", "rejected", "expired"},
    "approved": set(),
    "rejected": set(),
    "expired": set(),
}


class AprovacaoError(Exception):
    """Decisão inválida (estado, papel, autoaprovação ou expiração)."""


@dataclass
class Aprovacao:
    id: str
    acao: str
    solicitante: str
    criada_em: datetime
    expira_em: datetime
    papel_minimo: str = "analista_redes"
    estado: str = "pending"
    decidida_por: str | None = None
    justificativa: str | None = None
    contexto: dict = field(default_factory=dict)
    versao: int = 1


class ApprovalService:
    def __init__(self, ttl: timedelta = timedelta(minutes=15), auditoria: AuditChain | None = None,
                 relogio: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
                 repository: StateRepository | None = None) -> None:
        self.ttl, self.auditoria, self.relogio = ttl, auditoria, relogio
        self._itens: dict[str, Aprovacao] = {}
        self._lock = threading.Lock()
        self.repository = repository

    def _persist(self, ap: Aprovacao, create: bool = False) -> None:
        if self.repository is not None:
            try:
                data = (self.repository.create("approvals", ap.id, snapshot(ap)) if create else
                        self.repository.save("approvals", ap.id, snapshot(ap), ap.versao))
                ap.versao = data["versao"]
            except StateConflict as exc:
                raise AprovacaoError(str(exc)) from exc

    @staticmethod
    def _restore(data: dict) -> Aprovacao:
        data = dict(data)
        for key in ("criada_em", "expira_em"):
            data[key] = datetime.fromisoformat(data[key])
        return Aprovacao(**data)

    def _log(self, ator: str, acao: str, ap: Aprovacao) -> None:
        if self.auditoria is not None:
            self.auditoria.registrar(ator, acao, f"approval:{ap.id}",
                                     {"acao": ap.acao, "estado": ap.estado, "justificativa": ap.justificativa})

    def solicitar(self, acao: str, solicitante: str, papel_minimo: str = "analista_redes",
                  contexto: dict | None = None) -> Aprovacao:
        if papel_minimo not in PAPEIS:
            raise ValueError(f"papel desconhecido: {papel_minimo}")
        agora = self.relogio()
        ap = Aprovacao(str(uuid.uuid4()), acao, solicitante, agora, agora + self.ttl, papel_minimo,
                       contexto=contexto or {})
        with self._lock:
            self._persist(ap, create=True)
            self._itens[ap.id] = ap
        self._log(solicitante, "approval.requested", ap)
        return ap

    def obter(self, approval_id: str) -> Aprovacao:
        try:
            ap = (self._restore(self.repository.get("approvals", approval_id))
                  if self.repository is not None else self._itens[approval_id])
        except KeyError:
            raise AprovacaoError("aprovação inexistente") from None
        self._expirar_se_preciso(ap)
        return ap

    def _expirar_se_preciso(self, ap: Aprovacao) -> None:
        if ap.estado == "pending" and self.relogio() >= ap.expira_em:
            ap.estado = "expired"
            self._persist(ap)
            self._log("system", "approval.expired", ap)

    def _decidir(self, approval_id: str, decisor: str, papel: str, novo: str, justificativa: str | None) -> Aprovacao:
        with self._lock:
            ap = self.obter(approval_id)
            if novo not in TRANSICOES[ap.estado]:
                raise AprovacaoError(f"transição inválida: {ap.estado} → {novo}")
            if papel not in PAPEIS:
                raise AprovacaoError(f"papel desconhecido: {papel}")
            if PAPEIS[papel] < PAPEIS[ap.papel_minimo]:
                raise AprovacaoError(f"papel insuficiente: exige {ap.papel_minimo}")
            if decisor == ap.solicitante:
                raise AprovacaoError("o solicitante não pode decidir a própria solicitação")
            ap.estado, ap.decidida_por, ap.justificativa = novo, decisor, justificativa
            self._persist(ap)
        self._log(decisor, f"approval.{novo}", ap)
        return ap

    def aprovar(self, approval_id: str, decisor: str, papel: str, justificativa: str | None = None) -> Aprovacao:
        return self._decidir(approval_id, decisor, papel, "approved", justificativa)

    def rejeitar(self, approval_id: str, decisor: str, papel: str, justificativa: str | None = None) -> Aprovacao:
        return self._decidir(approval_id, decisor, papel, "rejected", justificativa)

    def pendentes(self) -> list[Aprovacao]:
        if self.repository is not None:
            self._itens = {item["id"]: self._restore(item) for item in self.repository.list("approvals")}
        for ap in list(self._itens.values()):
            self._expirar_se_preciso(ap)
        return [a for a in self._itens.values() if a.estado == "pending"]
