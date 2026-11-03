"""Âncora externa da trilha de auditoria e verificação periódica (issue #13).

A cadeia de hash detecta alteração, mas quem apaga o arquivo inteiro e recomeça
produz uma cadeia nova e íntegra. A âncora guarda, fora do arquivo, quantas
entradas existiam e qual era o último hash. Se a cadeia atual for menor ou não
contiver aquele hash na posição ancorada, houve remoção ou reescrita.

Destinos: ``AncoraArquivo`` (caminho em outro volume ou servidor, legível pela
verificação) e ``AncoraWebhook`` (POST JSON, por exemplo para o n8n enviar e-mail
ao Gestor de TI; só publica, não lê de volta). A âncora tem apenas contagem, hash,
horário e id da chave: nenhum dado pessoal nem a chave.

Limite: quem controlar também o destino da âncora pode reescrevê-lo. O destino
deve ficar fora do alcance de quem opera a máquina da API.
"""

from __future__ import annotations

import hmac
import json
import logging
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol

from .audit_chain import AuditChain

logger = logging.getLogger("sigma.audit")

WEBHOOK_TIMEOUT_SECONDS = 5


class Destino(Protocol):
    def publicar(self, ancora: dict) -> None: ...

    def ultima(self) -> dict | None: ...


@dataclass(frozen=True)
class ResultadoVerificacao:
    integra: bool
    motivo: str | None
    entradas: int
    ancorada: bool


def verificar_contra_ancora(cadeia: AuditChain, ancora: dict | None) -> tuple[bool, str | None]:
    """(ok, motivo). Sem âncora prévia, não há o que comparar."""
    if ancora is None:
        return True, None
    try:
        n = ancora["entradas"]
        ultimo = ancora["ultimo_hash"]
    except (KeyError, TypeError):
        return False, "ancora_invalida"
    if not isinstance(n, int) or isinstance(n, bool) or n < 0 or not isinstance(ultimo, str):
        return False, "ancora_invalida"
    if n == 0:
        return True, None
    entradas = cadeia.entradas
    if len(entradas) < n:
        return False, "cadeia_menor_que_ancora"
    atual = entradas[n - 1].get("hash")
    if not isinstance(atual, str) or not hmac.compare_digest(atual, ultimo):
        return False, "hash_diferente_da_ancora"
    return True, None


class AncoraArquivo:
    """JSONL só de acréscimo. Aponte para outro volume ou servidor."""

    def __init__(self, caminho: str | os.PathLike) -> None:
        self.caminho = Path(caminho)

    def publicar(self, ancora: dict) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with self.caminho.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(ancora, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def ultima(self) -> dict | None:
        if not self.caminho.exists():
            return None
        ultima = None
        with self.caminho.open(encoding="utf-8") as fh:
            for linha in fh:
                try:
                    valor = json.loads(linha)
                except ValueError:
                    continue
                if isinstance(valor, dict):
                    ultima = valor
        return ultima


class AncoraWebhook:
    def __init__(self, url: str, timeout: float = WEBHOOK_TIMEOUT_SECONDS) -> None:
        partes = urllib.parse.urlsplit(url)
        if partes.scheme not in ("http", "https") or not partes.netloc:
            raise ValueError("URL do webhook deve ser http(s).")
        self.url = url
        self.timeout = timeout

    def enviar(self, payload: dict) -> None:
        req = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            if not 200 <= resp.status < 300:
                raise OSError("Webhook recusou a mensagem.")

    def publicar(self, ancora: dict) -> None:
        self.enviar({"tipo": "audit.ancora", **ancora})

    def ultima(self) -> dict | None:
        return None


def executar_verificacao(cadeia: AuditChain, destinos: list[Destino],
                         alerta: Callable[[dict], None] | None = None) -> ResultadoVerificacao:
    """Verifica a cadeia e a compara com a última âncora de cada destino legível.

    Íntegra: publica nova âncora. Não íntegra: avisa e NÃO avança a âncora, para a
    evidência da divergência não ser sobrescrita.
    """
    resumo = cadeia.resumo()
    motivo = None if resumo["integra"] else "cadeia_invalida"
    if motivo is None:
        for destino in destinos:
            try:
                ok, motivo = verificar_contra_ancora(cadeia, destino.ultima())
            except Exception as exc:
                logger.warning("AUDIT_ANCHOR leitura falhou: %s", type(exc).__name__)
                continue
            if not ok:
                break
    if motivo is not None:
        _avisar(alerta, {"tipo": "audit.integridade_falhou", "motivo": motivo,
                         "entradas": resumo["entradas"], "ts": datetime.now(timezone.utc).isoformat()})
        return ResultadoVerificacao(False, motivo, resumo["entradas"], False)
    ancora = cadeia.ancora()
    publicou = False
    for destino in destinos:
        try:
            destino.publicar(ancora)
            publicou = True
        except Exception as exc:
            logger.warning("AUDIT_ANCHOR publicação falhou: %s", type(exc).__name__)
    if destinos and not publicou:
        _avisar(alerta, {"tipo": "audit.ancora_falhou", "motivo": "nenhum_destino",
                         "entradas": resumo["entradas"], "ts": datetime.now(timezone.utc).isoformat()})
    return ResultadoVerificacao(True, None, resumo["entradas"], publicou)


def _avisar(alerta: Callable[[dict], None] | None, payload: dict) -> None:
    logger.error("AUDIT_INTEGRITY event=%s motivo=%s", payload["tipo"], payload["motivo"])
    if alerta is None:
        return
    try:
        alerta(payload)
    except Exception as exc:
        # Falha do canal de alerta não pode esconder o resultado da verificação.
        logger.error("AUDIT_ALERT envio falhou: %s", type(exc).__name__)


def destinos_do_ambiente(env: dict[str, str] | None = None) -> tuple[list[Destino], Callable[[dict], None] | None]:
    """(destinos, alerta) de ``SIGMA_AUDIT_ANCHOR_PATH`` e ``SIGMA_AUDIT_ANCHOR_WEBHOOK``."""
    env = os.environ if env is None else env
    destinos: list[Destino] = []
    alerta = None
    caminho = (env.get("SIGMA_AUDIT_ANCHOR_PATH") or "").strip()
    if caminho:
        destinos.append(AncoraArquivo(caminho))
    url = (env.get("SIGMA_AUDIT_ANCHOR_WEBHOOK") or "").strip()
    if url:
        webhook = AncoraWebhook(url)
        destinos.append(webhook)
        alerta = webhook.enviar
    return destinos, alerta
