"""Configuração da API validada antes de atender requisições."""

import os
import re
from dataclasses import dataclass, field
from ipaddress import IPv6Address
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv


class ConfigurationError(RuntimeError):
    """Configuração inválida; as mensagens nunca incluem seus valores."""


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str = field(repr=False)
    llm_model: str
    cors_origins: tuple[str, ...]


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigurationError(f"Configure a variável obrigatória {name}.")
    return value


def _is_origin(value: str) -> bool:
    # Uma origem não contém caminho, credenciais, query ou fragmento.
    if not re.fullmatch(
        r"https?://(?:[A-Za-z0-9.-]+|\[[0-9A-Fa-f:]+\])(?::[0-9]{1,5})?",
        value,
    ):
        return False
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
        if port is not None and not 1 <= port <= 65535:
            return False
        if not host:
            return False
        if ":" in host:
            IPv6Address(host)
        elif len(host) > 253 or not all(
            re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
            for label in host.split(".")
        ):
            return False
    except ValueError:
        return False
    return True


def load_settings(env_file: Path | None = None) -> Settings:
    """Lê o .env da raiz sem substituir variáveis do processo."""
    path = env_file if env_file is not None else Path(__file__).resolve().with_name(".env")
    load_dotenv(dotenv_path=path, override=False, interpolate=False, encoding="utf-8-sig")

    key = _required("OPENROUTER_API_KEY")
    # Evita InvalidHeader/UnicodeEncodeError que poderiam refletir a chave na
    # mensagem de erro legada da rota. Valide antes de criar qualquer requisição.
    if not key.isascii() or any(not 33 <= ord(char) <= 126 for char in key):
        raise ConfigurationError(
            "OPENROUTER_API_KEY deve conter somente caracteres ASCII visíveis, sem espaços."
        )
    model = _required("SIGMA_LLM_MODEL")
    origins = tuple(origin.strip() for origin in _required("SIGMA_CORS_ORIGINS").split(","))
    if not all(_is_origin(origin) for origin in origins):
        raise ConfigurationError(
            "SIGMA_CORS_ORIGINS deve conter origens HTTP/HTTPS explícitas, "
            "separadas por vírgulas, sem curingas, caminhos ou credenciais."
        )
    return Settings(key, model, origins)
