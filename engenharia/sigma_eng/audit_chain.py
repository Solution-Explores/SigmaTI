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
import errno
import hmac
import json
import os
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

GENESIS = "0" * 64
LOCK_TIMEOUT_SECONDS = 10


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
        if self.caminho:
            with self._coordenar():
                pass

    @contextmanager
    def _coordenar(self):
        """Lock lateral estável: coordena instâncias e processos cooperantes."""
        with self._lock:
            if self.caminho is None:
                yield
                return
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            resolved = self.caminho.resolve()
            lock_path = resolved.with_name(resolved.name + ".lock")
            with open(lock_path, "a+b") as lock:
                # Windows permite bloquear além do EOF; não inicializar bytes
                # fora do lock, evitando outra corrida no primeiro uso.
                deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
                while True:
                    try:
                        lock.seek(0)
                        if os.name == "nt":
                            import msvcrt
                            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                        else:
                            import fcntl
                            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except OSError as exc:
                        if exc.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                            raise
                        if time.monotonic() >= deadline:
                            raise TimeoutError("Auditoria ocupada.") from None
                        time.sleep(0.01)
                try:
                    if self.caminho.exists():
                        # Binário + decodificação por linha: byte UTF-8 inválido
                        # vira entrada inválida e a verificação o reporta, em vez
                        # de lançar UnicodeDecodeError e derrubar o endpoint.
                        with self.caminho.open("rb") as stream:
                            self._entradas = []
                            for line in stream:
                                if line.strip():
                                    try:
                                        row = json.loads(line.decode("utf-8"))
                                    except ValueError:
                                        row = {}
                                    self._entradas.append(row if isinstance(row, dict) else {})
                    else:
                        self._entradas = []
                    yield
                finally:
                    # Falha no unlock não deve mascarar a exceção original;
                    # o close() do handle libera o bloqueio de qualquer forma.
                    try:
                        lock.seek(0)
                        if os.name == "nt":
                            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                        else:
                            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                    except OSError:
                        pass

    def __bool__(self) -> bool:
        return True

    def _hash(self, corpo: dict) -> str:
        dados = _canonico(corpo)
        if self.chave:
            return hmac.new(self.chave, dados, hashlib.sha256).hexdigest()
        return hashlib.sha256(dados).hexdigest()

    def registrar(self, ator: str, acao: str, recurso: str | None = None, detalhes: dict | None = None) -> dict:
        """Anexa um evento e devolve a entrada (com ``hash``)."""
        with self._coordenar():
            if not self._verificar()[0]:
                raise ValueError("Trilha de auditoria inválida; gravação recusada.")
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
                with self.caminho.open("a+b") as fh:
                    fh.seek(0, os.SEEK_END)
                    if fh.tell():
                        fh.seek(-1, os.SEEK_END)
                        if fh.read(1) != b"\n":
                            fh.write(b"\n")
                    fh.write((json.dumps(entrada, ensure_ascii=False) + "\n").encode("utf-8"))
                    fh.flush()
                    os.fsync(fh.fileno())
            self._entradas.append(entrada)
            return entrada

    def verificar(self) -> tuple[bool, int | None]:
        """(íntegra?, índice da primeira entrada inválida)."""
        with self._coordenar():
            return self._verificar()

    def resumo(self) -> dict:
        """Contagem e integridade pertencem à mesma leitura protegida."""
        with self._coordenar():
            ok, indice = self._verificar()
            return {"integra": ok, "primeira_invalida": indice, "entradas": len(self._entradas)}

    def _verificar(self) -> tuple[bool, int | None]:
        anterior = GENESIS
        for i, e in enumerate(self._entradas):
            corpo = {k: v for k, v in e.items() if k != "hash"}
            if e.get("seq") != i or e.get("anterior") != anterior:
                return False, i
            actual = e.get("hash")
            if not isinstance(actual, str) or not actual.isascii() or not hmac.compare_digest(self._hash(corpo), actual):
                return False, i
            anterior = e["hash"]
        return True, None

    @property
    def entradas(self) -> list[dict]:
        with self._coordenar():
            return json.loads(json.dumps(self._entradas))

    def __len__(self) -> int:
        with self._coordenar():
            return len(self._entradas)
