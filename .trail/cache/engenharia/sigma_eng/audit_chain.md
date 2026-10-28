# engenharia/sigma_eng/audit_chain.py

- _canonico · function · L27-L28 — def _canonico(obj: Any) -> bytes
- AuditChain · class · L31-L92 — class AuditChain
- __init__ · method · L32-L41 — def __init__(self, caminho: str | os.PathLike | None = None, chave: bytes | None = None, relogio: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> None
- __bool__ · method · L43-L44 — def __bool__(self) -> bool
- _hash · method · L46-L50 — def _hash(self, corpo: dict) -> str
- registrar · method · L52-L73 — def registrar(self, ator: str, acao: str, recurso: str | None = None, detalhes: dict | None = None) -> dict
- verificar · method · L75-L85 — def verificar(self) -> tuple[bool, int | None]
- entradas · method · L88-L89 — def entradas(self) -> list[dict]
- __len__ · method · L91-L92 — def __len__(self) -> int
