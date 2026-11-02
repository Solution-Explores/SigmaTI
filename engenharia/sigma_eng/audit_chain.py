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

Custo (#46): ``verificar()`` e ``resumo()`` percorrem a trilha inteira, de propósito. Já
``registrar()``, ``ancora()`` e ``len()`` guardam em memória, por arquivo e por processo, o
estado verificado (contagem, último hash e o SHA-256 dos bytes verificados) e, a cada chamada,
só leem e conferem o que foi acrescentado. Qualquer mudança no trecho já verificado (editar,
reordenar, trocar o arquivo) invalida esse estado e força a verificação completa, que então
recusa a gravação. Detalhes e limite do cache em ``_Estado.confiavel``.

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
# Quanto tempo o estado verificado vale sem reconferir os bytes (0 = sempre reconferir).
REVALIDAR_CONTEUDO_SEGUNDOS = 30
# Escrita recente demais para confiar no timestamp do arquivo (mesma ideia do "racy git"): o
# relógio do sistema de arquivos pode ser grosso (ms a dezenas de ms) e uma edição do mesmo
# tamanho logo após a nossa escrita manteria o timestamp.
JANELA_TIMESTAMP_NS = 100_000_000
_BLOCO = 1 << 20

_ESTADOS: dict[tuple, "_Estado"] = {}


def _agora_ns() -> int:
    return time.time_ns()


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


class _Estado:
    """O que já foi verificado de um arquivo: tamanho, contagem, último hash e SHA-256 dos bytes."""

    __slots__ = ("tamanho", "mtime_ns", "ino", "dev", "contagem", "ultimo_hash", "ultimo_kid", "digest",
                 "conferido_em")

    def __init__(self, st: os.stat_result | None, tamanho: int, contagem: int, ultimo_hash: str,
                 ultimo_kid: str | None, digest) -> None:
        self.tamanho = tamanho
        self.mtime_ns = st.st_mtime_ns if st else 0
        self.ino = st.st_ino if st else 0
        self.dev = st.st_dev if st else 0
        self.contagem = contagem
        self.ultimo_hash = ultimo_hash
        self.ultimo_kid = ultimo_kid
        self.digest = digest
        self.conferido_em = time.monotonic()

    @classmethod
    def vazio(cls) -> "_Estado":
        return cls(None, 0, 0, GENESIS, None, hashlib.sha256())

    def confiavel(self, st: os.stat_result) -> bool:
        """Dá para usar o estado sem reler o arquivo?

        Só se o arquivo não mudou (tamanho e timestamp), o estado foi conferido há pouco e a
        última escrita não é recente demais para o timestamp valer. Fora disso os bytes já
        verificados são reconferidos pelo SHA-256 (cerca de 100 ms para 30 MB).
        Limite: quem edita o arquivo, mantém o tamanho e restaura o timestamp só é pego na
        próxima reconferência (no máximo ``REVALIDAR_CONTEUDO_SEGUNDOS``) ou em ``verificar()``,
        que o job diário e a API executam por inteiro.
        """
        return (st.st_size == self.tamanho and st.st_mtime_ns == self.mtime_ns
                and time.monotonic() - self.conferido_em < REVALIDAR_CONTEUDO_SEGUNDOS
                and _agora_ns() - self.mtime_ns > JANELA_TIMESTAMP_NS)


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
        self._entradas: list[dict] = []  # só sem arquivo (trilha em memória)
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

    def _conferir(self, entrada: dict, indice: int, anterior: str) -> bool:
        """A entrada ``indice`` encadeia com ``anterior`` e tem o hash certo?"""
        if entrada.get("seq") != indice or entrada.get("anterior") != anterior:
            return False
        corpo = {k: v for k, v in entrada.items() if k != "hash"}
        atual = entrada.get("hash")
        esperado = self._hash(corpo)
        return not (esperado is None or not isinstance(atual, str) or not atual.isascii()
                    or not hmac.compare_digest(esperado, atual))

    @staticmethod
    def _linha(linha: bytes) -> dict:
        # Binário + decodificação por linha: byte UTF-8 inválido vira entrada inválida e a
        # verificação o reporta, em vez de lançar UnicodeDecodeError e derrubar o endpoint.
        try:
            entrada = json.loads(linha.decode("utf-8"))
        except ValueError:
            entrada = {}
        return entrada if isinstance(entrada, dict) else {}

    def _ler_tudo(self) -> list[dict]:
        """Todas as entradas (inclusive as inválidas, como ``{}``). O chamador detém o lock."""
        if self.caminho is None:
            return self._entradas
        if not self.caminho.exists():
            return []
        with self.caminho.open("rb") as fluxo:
            return [self._linha(linha) for linha in fluxo if linha.strip()]

    # --- Estado verificado em memória (#46) ---

    def _chave_cache(self) -> tuple:
        """Arquivo e chaves: outra chave ou outro arquivo nunca aproveita o estado alheio."""
        chaves = tuple(sorted((kid, hashlib.sha256(valor).hexdigest()) for kid, valor in self._chaves.items()))
        legada = hashlib.sha256(self._legada).hexdigest() if self._legada else None
        return str(self.caminho.resolve()), chaves, legada

    def _verificar_arquivo(self) -> tuple[bool, int | None, int, "_Estado | None"]:
        """Verificação completa em uma passagem: (íntegra, primeira inválida, total, estado se íntegra)."""
        digest = hashlib.sha256()
        anterior, kid, indice, invalida, lidos = GENESIS, None, 0, None, 0
        if not self.caminho.exists():
            return True, None, 0, _Estado.vazio()
        with self.caminho.open("rb") as fluxo:
            for linha in fluxo:
                digest.update(linha)
                lidos += len(linha)
                if not linha.strip():
                    continue
                entrada = self._linha(linha)
                if invalida is None:
                    if self._conferir(entrada, indice, anterior):
                        anterior, kid = entrada["hash"], entrada.get("kid")
                    else:
                        invalida = indice
                indice += 1
            st = os.fstat(fluxo.fileno())
        if invalida is not None:
            return False, invalida, indice, None
        return True, None, indice, _Estado(st, lidos, indice, anterior, kid, digest)

    def _avancar(self, estado: _Estado) -> _Estado | None:
        """Reconfere os bytes já verificados e verifica só o que foi acrescentado.

        None se o trecho antigo mudou, encolheu, ou o acréscimo é inválido: o chamador então
        faz a verificação completa, que dá o veredito e o índice.
        """
        continuacao = estado.digest.copy()
        with self.caminho.open("rb") as fluxo:
            conferido, restante = hashlib.sha256(), estado.tamanho
            while restante:
                bloco = fluxo.read(min(restante, _BLOCO))
                if not bloco:
                    return None
                conferido.update(bloco)
                restante -= len(bloco)
            if not hmac.compare_digest(conferido.digest(), continuacao.digest()):
                return None
            contagem, anterior, kid, lidos = estado.contagem, estado.ultimo_hash, estado.ultimo_kid, estado.tamanho
            for linha in fluxo:
                continuacao.update(linha)
                lidos += len(linha)
                if not linha.strip():
                    continue
                entrada = self._linha(linha)
                if not self._conferir(entrada, contagem, anterior):
                    return None
                anterior, kid = entrada["hash"], entrada.get("kid")
                contagem += 1
            st = os.fstat(fluxo.fileno())
        return _Estado(st, lidos, contagem, anterior, kid, continuacao)

    def _estado_verificado(self) -> _Estado:
        """Estado íntegro do arquivo com custo proporcional ao que mudou. ValueError se a trilha é inválida.

        O chamador detém o lock. Só vale para trilha em arquivo.
        """
        if not self.caminho.exists():
            return _Estado.vazio()
        chave = self._chave_cache()
        st = self.caminho.stat()
        estado = _ESTADOS.get(chave)
        if estado is not None and estado.ino == st.st_ino and estado.dev == st.st_dev \
                and st.st_size >= estado.tamanho:
            if estado.confiavel(st):
                return estado
            avancado = self._avancar(estado)
            if avancado is not None:
                _ESTADOS[chave] = avancado
                return avancado
        integra, _, _, novo = self._verificar_arquivo()
        if not integra:
            _ESTADOS.pop(chave, None)
            raise ValueError("Trilha de auditoria inválida; gravação recusada.")
        _ESTADOS[chave] = novo
        return novo

    # --- API ---

    def registrar(self, ator: str, acao: str, recurso: str | None = None, detalhes: dict | None = None) -> dict:
        """Anexa um evento e devolve a entrada (com ``hash``)."""
        with self._coordenar():
            return self._registrar(ator, acao, recurso, detalhes)

    def _registrar(self, ator: str, acao: str, recurso: str | None, detalhes: dict | None) -> dict:
        """Anexa a entrada; o chamador já detém o lock de ``_coordenar``."""
        if self.caminho is None:
            if not self._verificar_lista(self._entradas)[0]:
                raise ValueError("Trilha de auditoria inválida; gravação recusada.")
            seq = len(self._entradas)
            anterior = self._entradas[-1]["hash"] if self._entradas else GENESIS
            estado = None
        else:
            estado = self._estado_verificado()
            seq, anterior = estado.contagem, estado.ultimo_hash
        corpo = {
            "seq": seq,
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
                tamanho = fh.tell()
                carga = b""
                if tamanho:
                    fh.seek(-1, os.SEEK_END)
                    if fh.read(1) != b"\n":
                        carga = b"\n"
                carga += (json.dumps(entrada, ensure_ascii=False) + "\n").encode("utf-8")
                fh.write(carga)
                fh.flush()
                os.fsync(fh.fileno())
                st = os.fstat(fh.fileno())
            chave = self._chave_cache()
            if tamanho == estado.tamanho:
                continuacao = estado.digest.copy()
                continuacao.update(carga)
                _ESTADOS[chave] = _Estado(st, tamanho + len(carga), seq + 1, entrada["hash"],
                                          entrada.get("kid"), continuacao)
            else:
                # Alguém escreveu fora do lock entre a verificação e a gravação: não aproveitar nada.
                _ESTADOS.pop(chave, None)
        else:
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

    def _contagem_e_ultima(self) -> tuple[int, str, str | None]:
        """(entradas, último hash, ``kid`` da última) para âncora e ``len``.

        Trilha inválida não impede a leitura: sem estado verificado, lê tudo como antes.
        """
        if self.caminho is not None:
            try:
                estado = self._estado_verificado()
                return estado.contagem, estado.ultimo_hash, estado.ultimo_kid
            except ValueError:
                pass
        entradas = self._ler_tudo()
        ultima = entradas[-1] if entradas else {}
        return len(entradas), ultima.get("hash", GENESIS), ultima.get("kid")

    def ancora(self) -> dict:
        """Resumo do estado atual para guardar fora da máquina (sem dados pessoais)."""
        with self._coordenar():
            total, ultimo_hash, kid = self._contagem_e_ultima()
            return {"entradas": total, "ultimo_hash": ultimo_hash,
                    "ts": self.relogio().isoformat(), "kid": kid}

    def verificar(self) -> tuple[bool, int | None]:
        """(íntegra?, índice da primeira entrada inválida). Sempre percorre a trilha inteira."""
        with self._coordenar():
            return self._verificar()

    def resumo(self) -> dict:
        """Contagem e integridade pertencem à mesma leitura protegida."""
        with self._coordenar():
            ok, indice, total = self._verificar_completo()
            return {"integra": ok, "primeira_invalida": indice, "entradas": total}

    def _verificar(self) -> tuple[bool, int | None]:
        ok, indice, _ = self._verificar_completo()
        return ok, indice

    def _verificar_completo(self) -> tuple[bool, int | None, int]:
        if self.caminho is None:
            ok, indice = self._verificar_lista(self._entradas)
            return ok, indice, len(self._entradas)
        ok, indice, total, estado = self._verificar_arquivo()
        chave = self._chave_cache()
        if ok:
            _ESTADOS[chave] = estado
        else:
            _ESTADOS.pop(chave, None)
        return ok, indice, total

    def _verificar_lista(self, entradas: list[dict]) -> tuple[bool, int | None]:
        anterior = GENESIS
        for i, entrada in enumerate(entradas):
            if not self._conferir(entrada, i, anterior):
                return False, i
            anterior = entrada["hash"]
        return True, None

    @property
    def entradas(self) -> list[dict]:
        with self._coordenar():
            return json.loads(json.dumps(self._ler_tudo()))

    def __len__(self) -> int:
        with self._coordenar():
            return self._contagem_e_ultima()[0]
