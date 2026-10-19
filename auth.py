"""Módulo central de autenticação, JWT de sessão e RBAC (RF07).

Implementa:
- Hashing de senhas seguro (PBKDF2-HMAC-SHA256 com salt individual por usuário);
- Emissão e validação de JWT de sessão RFC 7519 (HS256) com tempo de expiração;
- Hierarquia de papéis RBAC idêntica ao approvals.py do SigmaTI:
    suporte_n1 (1) < analista_redes (2) < gestor_ti (3);
- Dependências FastAPI: `obter_usuario_atual` e `exige_papel(papel_minimo)`;
- Proteção contra força bruta (máximo de 5 tentativas consecutivas com bloqueio temporário);
- Registro de auditoria seguro na AuditChain.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import time
import uuid
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from fastapi import Depends, Header, HTTPException, Request

logger = logging.getLogger("sigma.auth")

# Hierarquia de papéis oficial do SIGMA (idêntica a engenharia/sigma_eng/approvals.py)
PAPEIS: dict[str, int] = {
    "suporte_n1": 1,
    "analista_redes": 2,
    "gestor_ti": 3,
}

# Configurações de Sessão e Segurança
JWT_SECRET = None
_sessions: dict[str, dict] = {}
_session_lock = threading.Lock()
JWT_EXPIRATION_SECONDS = 3600
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900


# --- Funções Criptográficas Auxiliares (Base64URL e JWT puro sem dependências pesadas) ---

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode("ascii"))


def hash_senha(senha: str, salt: str | None = None) -> str:
    """Gera hash PBKDF2-HMAC-SHA256 seguro com salt criptográfico de 16 bytes."""
    salt_hex = salt or secrets.token_hex(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        bytes.fromhex(salt_hex),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt_hex}${derived.hex()}"


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Compara em tempo constante uma senha com o hash armazenado."""
    try:
        partes = hash_armazenado.split("$")
        if len(partes) != 4 or partes[0] != "pbkdf2_sha256":
            return False
        iterations = int(partes[1])
        salt_hex = partes[2]
        hash_esperado = partes[3]

        derived = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            bytes.fromhex(salt_hex),
            iterations,
        )
        return hmac.compare_digest(derived.hex(), hash_esperado)
    except Exception:
        return False


# --- Emissão e Validação de JWT RFC 7519 ---

class TokenError(HTTPException):
    def __init__(self, detail: str = "Autenticação necessária."):
        super().__init__(status_code=401, detail=detail)


def criar_token_sessao(
    usuario: str,
    papel: str,
    expira_em_segundos: int | None = None,
    secret_key: str | None = None,
) -> str:
    """Emite token JWT de sessão assinado com HS256 e expiração delimitada."""
    agora = int(time.time())
    if expira_em_segundos is None:
        expira_em_segundos = JWT_EXPIRATION_SECONDS
    key = secret_key or JWT_SECRET
    if not key:
        raise RuntimeError("Configure SIGMA_JWT_SECRET antes de emitir sessões.")
    if papel not in PAPEIS or not usuario:
        raise ValueError("Usuário ou papel inválido.")
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": usuario,
        "papel": papel,
        "iat": agora,
        "exp": agora + expira_em_segundos,
        "jti": str(uuid.uuid4()),
    }

    h_bytes = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_bytes = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    assinatura = hmac.new(
        key.encode("utf-8"),
        f"{h_bytes}.{p_bytes}".encode("ascii"),
        hashlib.sha256,
    ).digest()
    s_bytes = _b64url_encode(assinatura)

    with _session_lock:
        for jti in [j for j, sessao in _sessions.items() if sessao["exp"] <= agora]:
            _sessions.pop(jti, None)
        _sessions[payload["jti"]] = payload.copy()
    return f"{h_bytes}.{p_bytes}.{s_bytes}"


def decodificar_token_sessao(token: str, secret_key: str | None = None) -> dict:
    """Verifica e decodifica um JWT de sessão HS256."""
    try:
        key = secret_key or JWT_SECRET
        if not key:
            raise TokenError()
        partes = token.strip().split(".")
        if len(partes) != 3:
            raise TokenError("Token malformado.")

        h_bytes, p_bytes, s_bytes = partes

        # Valida assinatura em tempo constante
        assinatura_esperada = hmac.new(
            key.encode("utf-8"),
            f"{h_bytes}.{p_bytes}".encode("ascii"),
            hashlib.sha256,
        ).digest()

        if not hmac.compare_digest(_b64url_encode(assinatura_esperada), s_bytes):
            raise TokenError("Assinatura do token inválida.")

        header = json.loads(_b64url_decode(h_bytes).decode("utf-8"))
        if header.get("alg") != "HS256":
            raise TokenError("Algoritmo de token não suportado.")

        payload = json.loads(_b64url_decode(p_bytes).decode("utf-8"))

        agora = int(time.time())
        exp = payload.get("exp", 0)
        if type(exp) is not int or agora >= exp:
            raise TokenError("Token expirado.")

        if not isinstance(payload.get("sub"), str) or payload.get("papel") not in PAPEIS:
            raise TokenError()
        if not isinstance(payload.get("jti"), str) or type(payload.get("iat")) is not int:
            raise TokenError()
        with _session_lock:
            if _sessions.get(payload["jti"]) != payload:
                raise TokenError("Sessão encerrada.")

        return payload

    except TokenError:
        raise
    except Exception as exc:
        logger.warning("Falha ao decodificar token JWT: %s", type(exc).__name__)
        raise TokenError("Token inválido ou corrompido.") from exc


# --- Modelos e Repositório de Usuários ---

@dataclass
class Usuario:
    username: str
    senha_hash: str
    papel: str
    ativo: bool = True


class UsuarioRepository:
    """Gerencia usuários (compatível com persistência em PostgreSQL / in-memory)."""

    def __init__(self):
        self._usuarios: dict[str, Usuario] = {}

    def carregar(self, caminho: str) -> None:
        """Carrega hashes de um arquivo local; nenhum usuário é criado implicitamente."""
        from config import ConfigurationError
        try:
            dados = json.loads(Path(caminho).read_text(encoding="utf-8-sig"))
            if not isinstance(dados, list) or not dados:
                raise ValueError()
            usuarios = {}
            for item in dados:
                user = Usuario(**item)
                if (not isinstance(user.username, str) or not 1 <= len(user.username) <= 100
                        or user.papel not in PAPEIS or type(user.ativo) is not bool
                        or user.username in usuarios):
                    raise ValueError()
                partes = user.senha_hash.split("$")
                if (len(partes) != 4 or partes[0] != "pbkdf2_sha256"
                        or not 100_000 <= int(partes[1]) <= 1_000_000
                        or len(bytes.fromhex(partes[2])) < 16
                        or len(bytes.fromhex(partes[3])) != 32):
                    raise ValueError()
                usuarios[user.username] = user
            self._usuarios = usuarios
        except Exception:
            raise ConfigurationError("SIGMA_USERS_FILE deve apontar para usuários e hashes válidos.") from None

    def adicionar_usuario(self, username: str, senha_clara: str, papel: str) -> Usuario:
        if papel not in PAPEIS:
            raise ValueError(f"Papel desconhecido: {papel}")
        user = Usuario(
            username=username,
            senha_hash=hash_senha(senha_clara),
            papel=papel,
            ativo=True,
        )
        # Recriar uma conta não pode preservar as sessões da identidade anterior.
        with _session_lock:
            for jti in [j for j, sessao in _sessions.items()
                        if self is usuario_repo and sessao["sub"] == username]:
                _sessions.pop(jti, None)
            self._usuarios[username] = user
        return user

    def obter_por_username(self, username: str) -> Usuario | None:
        return self._usuarios.get(username)


usuario_repo = UsuarioRepository()


def configure_auth(secret: str) -> None:
    """Executado depois de load_settings, antes de registrar os roteadores."""
    from config import ConfigurationError
    global JWT_SECRET, JWT_EXPIRATION_SECONDS
    caminho = os.getenv("SIGMA_USERS_FILE", "").strip()
    if not caminho:
        raise ConfigurationError("Configure a variável obrigatória SIGMA_USERS_FILE.")
    def positive_setting(name: str, default: int, maximum: int) -> int:
        try:
            value = int(os.getenv(name, str(default)))
            if not 1 <= value <= maximum:
                raise ValueError()
            return value
        except ValueError:
            raise ConfigurationError(f"{name} deve estar entre 1 e {maximum}.") from None

    expiration = positive_setting("SIGMA_JWT_EXPIRATION_SECONDS", 3600, 86400)
    attempts = positive_setting("SIGMA_MAX_LOGIN_ATTEMPTS", 5, 100)
    duration = positive_setting("SIGMA_LOCKOUT_DURATION_SECONDS", 900, 86400)
    usuario_repo.carregar(caminho)
    JWT_EXPIRATION_SECONDS = expiration
    JWT_SECRET = secret
    rate_limiter.max_falhas = attempts
    rate_limiter.tempo_bloqueio = duration
    rate_limiter._tentativas.clear()
    with _session_lock:
        _sessions.clear()


def revogar_token(token: str) -> None:
    payload = decodificar_token_sessao(token)
    with _session_lock:
        _sessions.pop(payload["jti"], None)


# --- Limite de Tentativas (Rate Limiting contra Força Bruta) ---

@dataclass
class RegistroTentativa:
    falhas: int = 0
    bloqueado_ate: float = 0.0


class LoginRateLimiter:
    def __init__(self, max_falhas: int = MAX_LOGIN_ATTEMPTS, tempo_bloqueio: int = LOCKOUT_DURATION_SECONDS):
        self.max_falhas = max_falhas
        self.tempo_bloqueio = tempo_bloqueio
        self._tentativas: dict[str, RegistroTentativa] = {}

    def esta_bloqueado(self, chave: str) -> bool:
        registro = self._tentativas.get(chave)
        if not registro:
            return False
        agora = time.time()
        if agora < registro.bloqueado_ate:
            return True
        if registro.bloqueado_ate > 0:
            # Tempo de bloqueio expirou, reseta o registro
            self.limpar(chave)
        return False

    def registrar_falha(self, chave: str) -> tuple[int, bool]:
        """Registra falha e devolve (contagem_falhas, esta_bloqueado_agora)."""
        registro = self._tentativas.setdefault(chave, RegistroTentativa())
        registro.falhas += 1
        if registro.falhas >= self.max_falhas:
            registro.bloqueado_ate = time.time() + self.tempo_bloqueio
            return registro.falhas, True
        return registro.falhas, False

    def limpar(self, chave: str):
        self._tentativas.pop(chave, None)


rate_limiter = LoginRateLimiter()


# --- Integração com AuditChain ---

def obter_auditor():
    """Obtém a AuditChain instalada; falha sem expor detalhes sensíveis."""
    try:
        from sigma_eng.audit_chain import AuditChain
        caminho = os.getenv("SIGMA_AUDIT_PATH", "resultados/audit.jsonl")
        chave = os.getenv("SIGMA_AUDIT_KEY")
        return AuditChain(caminho, chave=chave.encode() if chave else None)
    except Exception as exc:
        logger.warning("Falha ao inicializar AuditChain: %s", type(exc).__name__)
        return None


# --- Dependências FastAPI para RBAC ---

def obter_usuario_atual(request: Request, authorization: str | None = Header(None)) -> Usuario:
    """Extrai e valida o token Bearer JWT da requisição."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Autenticação necessária.")

    token = authorization.split(" ", 1)[1].strip()
    payload = decodificar_token_sessao(token)

    username = payload.get("sub")
    papel = payload.get("papel")

    if not username or not papel:
        raise HTTPException(status_code=401, detail="Autenticação necessária.")

    usuario = usuario_repo.obter_por_username(username)
    if not usuario or not usuario.ativo or usuario.papel != papel:
        raise TokenError()
    return usuario


def exige_papel(papel_minimo: str) -> Callable:
    """Dependency factory que implementa a checagem RBAC da matriz do README."""
    if papel_minimo not in PAPEIS:
        raise ValueError(f"Papel desconhecido: {papel_minimo}")

    def _validador_papel(usuario: Usuario = Depends(obter_usuario_atual)) -> Usuario:
        nivel_usuario = PAPEIS.get(usuario.papel, 0)
        nivel_exigido = PAPEIS.get(papel_minimo, 999)

        if nivel_usuario < nivel_exigido:
            # 403 Forbidden para papel insuficiente
            raise HTTPException(status_code=403, detail="Requisição não permitida.")

        return usuario

    return _validador_papel
