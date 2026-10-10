"""Runbooks executáveis em Markdown, com dry-run, allowlist e aprovação por passo.

Decisão deliberada de segurança: o comando é quebrado com ``shlex`` e
executado **sem shell**, apenas se o executável estiver na allowlist, e os
valores de variáveis são validados contra injeção de argumentos. Dry-run é o
padrão.

Formato do passo::

    ```sigma:step{id=ping, requires_approval=false, timeout=10s}
    ping -c 3 ${HOST}
    ```
"""

from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import dataclass, field
from typing import Callable, Sequence

from .approvals import Aprovacao

_PASSO = re.compile(r"```sigma:step\{([^}]*)\}\n(.*?)```", re.DOTALL)
_ATTR = re.compile(r"(\w+)\s*=\s*([^,}\s]+)")
_VAR = re.compile(r"\$\{(\w+)\}")
_VALOR_SEGURO = re.compile(r"^[A-Za-z0-9_.:/@=-]{1,128}$")


class RunbookError(Exception):
    pass


@dataclass(frozen=True)
class Passo:
    id: str
    comando: str
    requer_aprovacao: bool = False
    timeout_s: int = 30


@dataclass
class ResultadoPasso:
    passo_id: str
    ok: bool
    saida: str = ""
    erro: str = ""
    codigo: int = 0
    simulado: bool = False


@dataclass
class Execucao:
    id: str
    passos: list[Passo]
    variaveis: dict[str, str]
    dry_run: bool
    status: str = "running"  # running | waiting_approval | completed | failed
    resultados: list[ResultadoPasso] = field(default_factory=list)
    aguardando: str | None = None  # id do passo que espera aprovação


def _timeout(valor: str) -> int:
    m = re.fullmatch(r"(\d+)([sm]?)", valor.strip())
    if not m:
        return 30
    n = int(m.group(1))
    return n * 60 if m.group(2) == "m" else n


def parsear(markdown: str) -> list[Passo]:
    passos: list[Passo] = []
    for m in _PASSO.finditer(markdown):
        attrs = dict(_ATTR.findall(m.group(1)))
        passos.append(Passo(
            id=attrs.get("id", f"passo_{len(passos)}"),
            comando=m.group(2).strip(),
            requer_aprovacao=attrs.get("requires_approval", "false").lower() == "true",
            timeout_s=_timeout(attrs.get("timeout", "30s")),
        ))
    ids = [p.id for p in passos]
    if len(ids) != len(set(ids)):
        raise RunbookError("ids de passo duplicados")
    return passos


def interpolar(comando: str, variaveis: dict[str, str]) -> str:
    for nome, valor in variaveis.items():
        if not _VALOR_SEGURO.match(valor) or valor.startswith("-"):
            raise RunbookError(f"valor inseguro para a variável {nome!r}")
    faltando = [v for v in _VAR.findall(comando) if v not in variaveis]
    if faltando:
        raise RunbookError(f"variáveis não resolvidas: {', '.join(sorted(set(faltando)))}")
    return _VAR.sub(lambda m: variaveis[m.group(1)], comando)


Executor = Callable[[Sequence[str], int], ResultadoPasso]


def executor_subprocess(argv: Sequence[str], timeout_s: int) -> ResultadoPasso:
    try:
        proc = subprocess.run(list(argv), capture_output=True, text=True, timeout=timeout_s, shell=False)
    except subprocess.TimeoutExpired:
        return ResultadoPasso("", False, erro=f"timeout após {timeout_s}s", codigo=124)
    except OSError as exc:
        return ResultadoPasso("", False, erro=str(exc), codigo=127)
    return ResultadoPasso("", proc.returncode == 0, proc.stdout, proc.stderr, proc.returncode)


class RunbookRunner:
    def __init__(self, allowlist: Sequence[str], executor: Executor = executor_subprocess) -> None:
        self.allowlist = set(allowlist)
        self.executor = executor

    def _argv(self, passo: Passo, variaveis: dict[str, str]) -> list[str]:
        argv = shlex.split(interpolar(passo.comando, variaveis))
        if not argv:
            raise RunbookError(f"passo {passo.id!r} vazio")
        if argv[0] not in self.allowlist:
            raise RunbookError(f"executável fora da allowlist: {argv[0]!r}")
        return argv

    def validar(self, passos: Sequence[Passo], variaveis: dict[str, str]) -> None:
        """Valida tudo antes de executar qualquer passo (falha cedo, não pela metade)."""
        for p in passos:
            self._argv(p, variaveis)

    def executar(self, execucao_id: str, passos: Sequence[Passo], variaveis: dict[str, str],
                 dry_run: bool = True) -> Execucao:
        self.validar(passos, variaveis)
        ex = Execucao(execucao_id, list(passos), dict(variaveis), dry_run)
        return self._seguir(ex)

    def retomar(self, ex: Execucao, aprovacao: Aprovacao) -> Execucao:
        if ex.status != "waiting_approval" or ex.aguardando is None:
            raise RunbookError("execução não está aguardando aprovação")
        if aprovacao.estado != "approved" or aprovacao.acao != f"runbook:{ex.id}:{ex.aguardando}":
            raise RunbookError("aprovação ausente, não concedida ou de outro passo")
        ex.status, ex.aguardando = "running", None
        return self._seguir(ex, aprovado=True)

    def _seguir(self, ex: Execucao, aprovado: bool = False) -> Execucao:
        for passo in ex.passos[len(ex.resultados):]:
            if passo.requer_aprovacao and not aprovado and not ex.dry_run:
                ex.status, ex.aguardando = "waiting_approval", passo.id
                return ex
            aprovado = False  # a aprovação vale para um único passo
            argv = self._argv(passo, ex.variaveis)
            if ex.dry_run:
                res = ResultadoPasso(passo.id, True, saida=" ".join(shlex.quote(a) for a in argv), simulado=True)
            else:
                res = self.executor(argv, passo.timeout_s)
                res.passo_id = passo.id
            ex.resultados.append(res)
            if not res.ok:
                ex.status = "failed"
                return ex
        ex.status = "completed"
        return ex
