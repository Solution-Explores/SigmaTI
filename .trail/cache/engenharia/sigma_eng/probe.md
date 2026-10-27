# engenharia/sigma_eng/probe.py

- ProbeResult · class · L37-L53 — class ProbeResult
- as_dict · method · L45-L53 — def as_dict(self) -> dict[str, Any]
- _finding · function · L56-L57 — def _finding(code: str, severity: str, message: str) -> dict[str, str]
- is_target_allowed · function · L60-L74 — def is_target_allowed(host: str, allowed_networks: Iterable[str] = DEFAULT_ALLOWED_NETWORKS) -> bool
- _is_ip · function · L77-L82 — def _is_ip(host: str) -> bool
- _host_in_cert · function · L85-L93 — def _host_in_cert(host: str, dns_names: list[str]) -> bool
- parse_http · function · L96-L112 — def parse_http(raw: bytes) -> tuple[int | None, dict[str, str]]
- _cert_facts · function · L115-L135 — def _cert_facts(der: bytes, host: str) -> tuple[int | None, bool] | None
- _overall · function · L138-L141 — def _overall(findings: list[dict[str, str]]) -> str
- probe_service · function · L144-L233 — def probe_service( host: str, port: int, kind: str, tls_warn_days: int = 30, timeout: float = 3.0, connector: Callable[..., socket.socket] = socket.create_connection, ) -> ProbeResult
- ProbeStats · class · L237-L253 — class ProbeStats
- as_dict · method · L246-L253 — def as_dict(self) -> dict[str, Any]
- probe_many · function · L256-L285 — def probe_many( host: str, port: int, kind: str = "tcp", count: int = 20, interval_s: float = 0.0, sleep: Callable[[float], None] = time.sleep, **kwargs: Any, ) -> ProbeStats
