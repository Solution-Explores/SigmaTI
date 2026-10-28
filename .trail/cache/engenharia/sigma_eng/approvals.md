# engenharia/sigma_eng/approvals.py

- AprovacaoError · class · L31-L32 — class AprovacaoError(Exception)
- Aprovacao · class · L36-L46 — class Aprovacao
- ApprovalService · class · L49-L110 — class ApprovalService
- __init__ · method · L50-L54 — def __init__(self, ttl: timedelta = timedelta(minutes=15), auditoria: AuditChain | None = None, relogio: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> None
- _log · method · L56-L59 — def _log(self, ator: str, acao: str, ap: Aprovacao) -> None
- solicitar · method · L61-L71 — def solicitar(self, acao: str, solicitante: str, papel_minimo: str = "analista_redes", contexto: dict | None = None) -> Aprovacao
- obter · method · L73-L79 — def obter(self, approval_id: str) -> Aprovacao
- _expirar_se_preciso · method · L81-L84 — def _expirar_se_preciso(self, ap: Aprovacao) -> None
- _decidir · method · L86-L99 — def _decidir(self, approval_id: str, decisor: str, papel: str, novo: str, justificativa: str | None) -> Aprovacao
- aprovar · method · L101-L102 — def aprovar(self, approval_id: str, decisor: str, papel: str, justificativa: str | None = None) -> Aprovacao
- rejeitar · method · L104-L105 — def rejeitar(self, approval_id: str, decisor: str, papel: str, justificativa: str | None = None) -> Aprovacao
- pendentes · method · L107-L110 — def pendentes(self) -> list[Aprovacao]
