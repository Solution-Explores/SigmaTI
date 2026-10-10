"""Sonda ativa de disponibilidade, latência e TLS (TCP / HTTP / HTTPS).

Características:
  * ``probe_many`` repete a medição e devolve perda, jitter e percentis;
  * ``is_target_allowed`` restringe alvos a redes autorizadas (anti-SSRF);
  * a verificação do certificado é opcional (depende de ``cryptography``);
  * o relógio e o conector são injetáveis, para teste determinístico.

As funções são bloqueantes de propósito: chame via ``asyncio.to_thread``.
"""

from __future__ import annotations

import ipaddress
import socket
import ssl
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterable

from .stats import mean, stdev, summary

# Redes que a sonda pode alcançar por padrão: loopback e RFC 1918 (LAN do hospital).
DEFAULT_ALLOWED_NETWORKS = (
    "127.0.0.0/8",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "::1/128",
)

VALID_KINDS = {"tcp", "http", "https"}


@dataclass
class ProbeResult:
    status: str  # up | degraded | down
    latency_ms: float | None = None
    http_status: int | None = None
    tls_days: int | None = None
    error: str | None = None
    findings: list[dict[str, str]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "latency_ms": self.latency_ms,
            "http_status": self.http_status,
            "tls_days": self.tls_days,
            "error": self.error,
            "findings": self.findings,
        }


def _finding(code: str, severity: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "message": message}


def is_target_allowed(host: str, allowed_networks: Iterable[str] = DEFAULT_ALLOWED_NETWORKS) -> bool:
    """True se *todos* os endereços do ``host`` caem em redes autorizadas.

    Exigir todos (e não algum) bloqueia DNS rebinding com respostas mistas.
    Falha de resolução conta como não autorizado.
    """
    nets = [ipaddress.ip_network(n) for n in allowed_networks]
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return False
    addrs = {ipaddress.ip_address(info[4][0]) for info in infos}
    if not addrs:
        return False
    return all(any(addr in net for net in nets) for addr in addrs)


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _host_in_cert(host: str, dns_names: list[str]) -> bool:
    host = host.lower().rstrip(".")
    for name in dns_names:
        candidate = name.lower().rstrip(".")
        if candidate == host:
            return True
        if candidate.startswith("*.") and host.endswith(candidate[1:]) and host.count(".") == candidate.count("."):
            return True
    return False


def parse_http(raw: bytes) -> tuple[int | None, dict[str, str]]:
    """Extrai código de status e cabeçalhos (minúsculos) de uma resposta HTTP."""
    text = raw.decode("iso-8859-1", errors="replace")
    head, _, _body = text.partition("\r\n\r\n")
    lines = head.split("\r\n")
    if not lines or " " not in lines[0]:
        return None, {}
    try:
        status = int(lines[0].split(" ")[1])
    except (IndexError, ValueError):
        status = None
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    return status, headers


def _cert_facts(der: bytes, host: str) -> tuple[int | None, bool] | None:
    """(dias até vencer, hostname coberto). ``None`` se ``cryptography`` faltar."""
    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
    except ImportError:
        return None
    cert = x509.load_der_x509_certificate(der, default_backend())
    not_after = getattr(cert, "not_valid_after_utc", None) or cert.not_valid_after
    if not_after.tzinfo is None:
        not_after = not_after.replace(tzinfo=timezone.utc)
    days = (not_after - datetime.now(timezone.utc)).days
    names: list[str] = []
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        names = list(ext.value.get_values_for_type(x509.DNSName))
    except x509.ExtensionNotFound:
        pass
    if not names:
        names = [str(a.value) for a in cert.subject if a.oid.dotted_string == "2.5.4.3"]
    return days, (True if _is_ip(host) else _host_in_cert(host, names))


def _overall(findings: list[dict[str, str]]) -> str:
    if any(f["severity"] in {"critical", "high", "medium"} for f in findings):
        return "degraded"
    return "up"


def probe_service(
    host: str,
    port: int,
    kind: str,
    tls_warn_days: int = 30,
    timeout: float = 3.0,
    connector: Callable[..., socket.socket] = socket.create_connection,
) -> ProbeResult:
    """Mede uma vez. A latência é o tempo do handshake TCP (SYN → ESTABLISHED)."""
    if kind not in VALID_KINDS:
        raise ValueError(f"kind inválido: {kind!r} (use {sorted(VALID_KINDS)})")
    if not 0 < port < 65536:
        raise ValueError("porta fora de 1-65535")

    started = time.perf_counter()
    try:
        sock = connector((host, port), timeout=timeout)
    except OSError as exc:
        return ProbeResult(
            status="down",
            error=str(exc),
            findings=[_finding("unreachable", "critical", f"Sem conexão TCP em {host}:{port}")],
        )

    latency_ms = round((time.perf_counter() - started) * 1000, 3)
    findings: list[dict[str, str]] = []
    http_status: int | None = None
    tls_days: int | None = None
    try:
        if kind == "tcp":
            return ProbeResult(status="up", latency_ms=latency_ms)

        if kind == "https":
            # Verificação desligada de propósito: a sonda *inspeciona* o
            # certificado (vencimento, hostname) em vez de recusá-lo.
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            sock = ctx.wrap_socket(sock, server_hostname=host)
            der = sock.getpeercert(binary_form=True)
            facts = _cert_facts(der, host) if der else None
            if facts is None:
                findings.append(_finding("tls_unchecked", "low", "Certificado não inspecionado (instale 'cryptography')"))
            else:
                tls_days, hostname_ok = facts
                if tls_days < 0:
                    findings.append(_finding("tls_expired", "critical", f"Certificado vencido há {-tls_days} dia(s)"))
                elif tls_days <= tls_warn_days:
                    findings.append(_finding("tls_expiring", "high", f"Certificado vence em {tls_days} dia(s)"))
                if not hostname_ok:
                    findings.append(_finding("tls_hostname", "medium", f"Certificado não cobre {host}"))

        request = f"GET / HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\nUser-Agent: SigmaProbe/0.1\r\n\r\n"
        sock.sendall(request.encode("ascii", errors="ignore"))
        sock.settimeout(timeout)
        chunks = bytearray()
        while len(chunks) < 16384:
            piece = sock.recv(4096)
            if not piece:
                break
            chunks.extend(piece)
        http_status, headers = parse_http(bytes(chunks))
        if http_status is None:
            findings.append(_finding("http_unreadable", "medium", "Porta aberta, mas a resposta HTTP não foi reconhecida"))
        elif http_status >= 500:
            findings.append(_finding("http_error", "high", f"HTTP {http_status}"))
        if http_status is not None:
            if kind == "https" and "strict-transport-security" not in headers:
                findings.append(_finding("hsts_missing", "medium", "HTTPS sem Strict-Transport-Security"))
            if "content-security-policy" not in headers:
                findings.append(_finding("csp_missing", "low", "Resposta sem Content-Security-Policy"))
        return ProbeResult(
            status=_overall(findings),
            latency_ms=latency_ms,
            http_status=http_status,
            tls_days=tls_days,
            findings=findings,
        )
    except OSError as exc:
        return ProbeResult(
            status="down",
            latency_ms=latency_ms,
            error=str(exc),
            findings=[_finding("unreachable", "critical", str(exc))],
        )
    finally:
        try:
            sock.close()
        except OSError:
            pass


@dataclass
class ProbeStats:
    """Resultado agregado de ``probe_many``."""

    samples: int
    failures: int
    loss_pct: float
    latency: dict[str, float]
    jitter_ms: float  # média de |Δ latência| entre amostras consecutivas (RFC 3550, simplificado)

    def as_dict(self) -> dict[str, Any]:
        return {
            "samples": self.samples,
            "failures": self.failures,
            "loss_pct": self.loss_pct,
            "latency": self.latency,
            "jitter_ms": self.jitter_ms,
        }


def probe_many(
    host: str,
    port: int,
    kind: str = "tcp",
    count: int = 20,
    interval_s: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
    **kwargs: Any,
) -> ProbeStats:
    """Repete ``probe_service`` ``count`` vezes e resume perda, latência e jitter."""
    if count < 1:
        raise ValueError("count deve ser >= 1")
    latencies: list[float] = []
    failures = 0
    for i in range(count):
        result = probe_service(host, port, kind, **kwargs)
        if result.status == "down" or result.latency_ms is None:
            failures += 1
        else:
            latencies.append(result.latency_ms)
        if interval_s and i < count - 1:
            sleep(interval_s)
    deltas = [abs(b - a) for a, b in zip(latencies, latencies[1:])]
    return ProbeStats(
        samples=count,
        failures=failures,
        loss_pct=round(100 * failures / count, 2),
        latency=summary(latencies),
        jitter_ms=round(mean(deltas), 3) if deltas else 0.0,
    )


__all__ = [
    "DEFAULT_ALLOWED_NETWORKS",
    "ProbeResult",
    "ProbeStats",
    "is_target_allowed",
    "parse_http",
    "probe_many",
    "probe_service",
    "stdev",
]
