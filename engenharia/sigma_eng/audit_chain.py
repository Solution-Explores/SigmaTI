"""Trilha de auditoria com cadeia de hash (tamper-evident).

Cada entrada inclui o hash
da anterior, então alterar, remover ou reordenar qualquer registro quebra a
verificação a partir dele. Com ``chave`` (HMAC-SHA256), quem edita o arquivo
sem a chave não consegue recalcular a cadeia; sem chave é SHA-256 simples,
que detecta corrupção e edição acidental, mas não um adversário que refaça
todos os hashes.

Formato JSONL, uma entrada por linha, anexado com fsync.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

GENESIS = "0" * 64


def _canonico(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class AuditChain:
    def __init__(self, caminho: str | os.PathLike | None = None, chave: bytes | None = None,
                 relogio: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> None:
        self.caminho = Path(caminho) if caminho else None
        self.chave = chave
        self.relogio = relogio
        self._lock = threading.Lock()
        self._entradas: list[dict] = []
        if self.caminho and self.caminho.exists():
            with self.caminho.open(encoding="utf-8") as fh:
                self._entradas = [json.loads(linha) for linha in fh if linha.strip()]

    def _hash(self, corpo: dict) -> str:
        dados = _canonico(corpo)
        if self.chave:
            return hmac.new(self.chave, dados, hashlib.sha256).hexdigest()
        return hashlib.sha256(dados).hexdigest()

    def registrar(self, ator: str, acao: str, recurso: str | None = None, detalhes: dict | None = None) -> dict:
        """Anexa um evento e devolve a entrada (com ``hash``)."""
        with self._lock:
            anterior = self._entradas[-1]["hash"] if self._entradas else GENESIS
            corpo = {
                "seq": len(self._entradas),
                "ts": self.relogio().isoformat(),
                "ator": ator,
                "acao": acao,
                "recurso": recurso,
                "detalhes": detalhes or {},
                "anterior": anterior,
            }
            entrada = {**corpo, "hash": self._hash(corpo)}
            if self.caminho:
                self.caminho.parent.mkdir(parents=True, exist_ok=True)
                with self.caminho.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entrada, ensure_ascii=False) + "\n")
                    fh.flush()
                    os.fsync(fh.fileno())
            self._entradas.append(entrada)
            return entrada

    def verificar(self) -> tuple[bool, int | None]:
        """(íntegra?, índice da primeira entrada inválida)."""
        anterior = GENESIS
        for i, e in enumerate(self._entradas):
            corpo = {k: v for k, v in e.items() if k != "hash"}
            if e.get("seq") != i or e.get("anterior") != anterior:
                return False, i
            if not hmac.compare_digest(self._hash(corpo), str(e.get("hash"))):
                return False, i
            anterior = e["hash"]
        return True, None

    @property
    def entradas(self) -> list[dict]:
        return list(self._entradas)

    def __len__(self) -> int:
        return len(self._entradas)
