# engenharia/sigma_eng/runbooks.py

- RunbookError · class · L31-L32 — class RunbookError(Exception)
- Passo · class · L36-L40 — class Passo
- ResultadoPasso · class · L44-L50 — class ResultadoPasso
- Execucao · class · L54-L61 — class Execucao
- _timeout · function · L64-L69 — def _timeout(valor: str) -> int
- parsear · function · L72-L85 — def parsear(markdown: str) -> list[Passo]
- interpolar · function · L88-L95 — def interpolar(comando: str, variaveis: dict[str, str]) -> str
- executor_subprocess · function · L101-L108 — def executor_subprocess(argv: Sequence[str], timeout_s: int) -> ResultadoPasso
- RunbookRunner · class · L111-L160 — class RunbookRunner
- __init__ · method · L112-L114 — def __init__(self, allowlist: Sequence[str], executor: Executor = executor_subprocess) -> None
- _argv · method · L116-L122 — def _argv(self, passo: Passo, variaveis: dict[str, str]) -> list[str]
- validar · method · L124-L127 — def validar(self, passos: Sequence[Passo], variaveis: dict[str, str]) -> None
- executar · method · L129-L133 — def executar(self, execucao_id: str, passos: Sequence[Passo], variaveis: dict[str, str], dry_run: bool = True) -> Execucao
- retomar · method · L135-L141 — def retomar(self, ex: Execucao, aprovacao: Aprovacao) -> Execucao
- _seguir · method · L143-L160 — def _seguir(self, ex: Execucao, aprovado: bool = False) -> Execucao
