"""Trilha de auditoria com cadeia de hash (tamper-evident).

Cada entrada inclui o hash
da anterior, então alterar, remover ou reordenar qualquer registro quebra a
verificação a partir dele. Com ``chave`` (HMAC-SHA256), quem edita o arquivo
sem a chave não consegue recalcular a cadeia; sem chave é SHA-256 simples,
que detecta corrupção e edição acidental, mas não um adversário que refaça
todos os hashes.

Rotação de chave: com ``chaves`` (id -> chave) e ``chave_ativa``, cada entrada nova
carrega ``kid`` (dentro do corpo assinado) e a verificação usa a chave daquele id.
Entradas anteriores sem ``kid`` usam ``chave_legada`` (por padrão, ``chave``).
Âncora externa: ``ancora()`` resume o último hash para guardar fora da máquina
(ver ``audit_anchor``); a cadeia sozinha não detecta apagar o arquivo inteiro.

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
from typing import Any, Callable, Mapping

GENESIS = "0" * 64
LOCK_TIMEOUT_SECONDS = 10


def chaves_do_ambiente(env: Mapping[str, str]) -> tuple[dict[str, bytes], str | None, bytes | None]:
    """(chaves por id, id ativo, chave legada) a partir do ambiente.

    Sem ``SIGMA_AUDIT_KEY_ID`` vale o formato anterior: uma chave, sem ``kid``.
    ``SIGMA_AUDIT_RETIRED_KEYS`` = "id:chave,id2:chave2"; ``SIGMA_AUDIT_LEGACY_KEY``
    verifica entradas gravadas antes da rotação (sem ``kid``).
    """
    chave = env.get("SIGMA_AUDIT_KEY") or None
    kid = (env.get("SIGMA_AUDIT_KEY_ID") or "").strip()
    if not kid:
        return {}, None, chave.encode() if chave else None
    if not chave:
        raise ValueError("SIGMA_AUDIT_KEY_ID exige SIGMA_AUDIT_KEY.")
    chaves = {kid: chave.encode()}
    for par in (env.get("SIGMA_AUDIT_RETIRED_KEYS") or "").split(","):
        if not par.strip():
            continue
        antigo, sep, valor = par.strip().partition(":")
        antigo = antigo.strip()
        if not sep or not antigo or not valor or antigo in chaves:
            raise ValueError("SIGMA_AUDIT_RETIRED_KEYS inválida.")
        chaves[antigo] = valor.encode()
    legada = env.get("SIGMA_AUDIT_LEGACY_KEY") or None
    return chaves, kid, legada.encode() if legada else None


def _canonico(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class AuditChain:
    def __init__(self, caminho: str | os.PathLike | None = None, chave: bytes | None = None,
                 relogio: Callable[[], datetime] = lambda: datetime.now(timezone.utc), *,
                 chaves: dict[str, bytes] | None = None, chave_ativa: str | None = None,
                 chave_legada: bytes | None = None) -> None:
        self.caminho = Path(caminho) if caminho else None
        self._chaves = dict(chaves or {})
        self._ativa = chave_ativa
        if self._ativa is not None and self._ativa not in self._chaves:
            raise ValueError("chave_ativa precisa estar em chaves.")
        # Entradas sem kid (formato anterior) usam a chave legada.
        self._legada = chave_legada if chave_legada is not None else chave
        self.chave = self._chaves[self._ativa] if self._ativa else chave
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

    @classmethod
    def do_ambiente(cls, caminho: str | os.PathLike, env: Mapping[str, str] | None = None) -> "AuditChain":
        chaves, ativa, legada = chaves_do_ambiente(os.environ if env is None else env)
        if ativa is None:
            return cls(caminho, chave=legada)
        return cls(caminho, chaves=chaves, chave_ativa=ativa, chave_legada=legada)

    @staticmethod
    def _assinar(chave: bytes | None, corpo: dict) -> str:
        dados = _canonico(corpo)
        if chave:
            return hmac.new(chave, dados, hashlib.sha256).hexdigest()
        return hashlib.sha256(dados).hexdigest()

    def _hash(self, corpo: dict) -> str | None:
        """Hash esperado com a chave do ``kid`` da entrada; None se a chave não está disponível."""
        kid = corpo.get("kid")
        if kid is None:
            return self._assinar(self._legada, corpo)
        if isinstance(kid, str) and kid in self._chaves:
            return self._assinar(self._chaves[kid], corpo)
        return None

    def registrar(self, ator: str, acao: str, recurso: str | None = None, detalhes: dict | None = None) -> dict:
        """Anexa um evento e devolve a entrada (com ``hash``)."""
        with self._coordenar():
            return self._registrar(ator, acao, recurso, detalhes)

    def _registrar(self, ator: str, acao: str, recurso: str | None, detalhes: dict | None) -> dict:
        """Anexa a entrada; o chamador já detém o lock de ``_coordenar``."""
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
        if self._ativa is not None:
            corpo["kid"] = self._ativa
        entrada = {**corpo, "hash": self._assinar(self.chave, corpo)}
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

    def rotacionar(self, novo_kid: str, nova_chave: bytes, ator: str) -> dict:
        """Troca a chave ativa. O evento de rotação é assinado pela chave anterior."""
        if not isinstance(novo_kid, str) or not novo_kid.strip() or not nova_chave:
            raise ValueError("Informe id e chave novos.")
        with self._coordenar():
            if novo_kid in self._chaves:
                raise ValueError("Id de chave já usado.")
            entrada = self._registrar(ator, "audit.key_rotated", "audit_key",
                                      {"de": self._ativa, "para": novo_kid})
            self._chaves[novo_kid] = nova_chave
            self._ativa = novo_kid
            self.chave = nova_chave
            return entrada

    def ancora(self) -> dict:
        """Resumo do estado atual para guardar fora da máquina (sem dados pessoais)."""
        with self._coordenar():
            ultima = self._entradas[-1] if self._entradas else {}
            return {"entradas": len(self._entradas), "ultimo_hash": ultima.get("hash", GENESIS),
                    "ts": self.relogio().isoformat(), "kid": ultima.get("kid")}

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
            esperado = self._hash(corpo)
            if esperado is None or not isinstance(actual, str) or not actual.isascii() \
                    or not hmac.compare_digest(esperado, actual):
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
