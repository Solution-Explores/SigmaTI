"""K10: aceite por HTTP real com Uvicorn e provedor de IA estritamente simulado.

Não aprova automaticamente o sistema: critérios não atendidos retornam exit 1.
Usa ambiente virtual do checkout indicado, credenciais fictícias e loopback.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
from dataclasses import asdict
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

FAKE_KEY = "fake-key-only-for-k10-acceptance"
PRIVATE_DETAIL = "private-k10-provider-detail"
ORIGIN = "http://localhost:5173"
ALERT = {"equipamento": "Switch de teste", "ip_origem": "192.0.2.10",
         "descricao_erro": "Falha dr.joao no IP 192.0.2.10 K10_OK"}


def serve(checkout: Path, port: int, events: Path) -> None:
    import asyncio

    sys.path.insert(0, str(checkout))
    sys.path.insert(0, str(checkout / "backend"))
    import httpx2 as httpx
    import uvicorn
    import main

    def event(phase: str) -> None:
        with events.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"phase": phase}) + "\n")

    async def provider(request):
        event("provider_called")
        content = request.content.decode()
        if "K10_TIMEOUT" in content:
            try:
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                event("provider_cancelled")
                raise
        if "K10_PROVIDER_ERROR" in content:
            return httpx.Response(503, text=PRIVATE_DETAIL)
        if "K10_INVALID_JSON" in content:
            return httpx.Response(200, text=PRIVATE_DETAIL)
        return httpx.Response(200, json={"choices": [{"message": {"content": "Diagnóstico K10 simulado"}}]})

    # Injeção confinada ao processo deste runner; main.py não é modificado.
    main.create_provider_client = lambda: httpx.AsyncClient(
        transport=httpx.MockTransport(provider), timeout=main.IA_TIMEOUT_SECONDS,
    )
    sanitizer = main.anonimizar_dados

    def sanitization(text):
        if "K10_SANITIZER_ERROR" in text:
            raise RuntimeError(PRIVATE_DETAIL)
        return sanitizer(text)

    main.anonimizar_dados = sanitization
    uvicorn.run(main.app, host="127.0.0.1", port=port, access_log=False, log_level="warning")


def request(base: str, method: str, path: str, payload=None, headers=None):
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base + path, data=body, method=method,
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=18) as response:
            return response.status, response.read().decode(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode(), dict(error.headers)


def validate(args) -> int:
    checkout = args.checkout.resolve()
    sys.path.insert(0, str(checkout))
    sys.path.insert(0, str(checkout / "backend"))
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    interpreter = checkout / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not interpreter.is_file():
        raise RuntimeError("Prepare the checkout virtual environment before acceptance")
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", args.port))
    env = {**os.environ, "OPENROUTER_API_KEY": FAKE_KEY, "SIGMA_LLM_MODEL": "test-provider/test-model",
           "SIGMA_CORS_ORIGINS": ORIGIN, "PYTHON_DOTENV_DISABLED": "1",
           "SIGMA_JWT_SECRET": secrets.token_hex(32), "SIGMA_AUDIT_KEY": secrets.token_hex(32),
           "SIGMA_AUDIT_PATH": str(output.with_suffix(".audit.jsonl")), "PYTHONUNBUFFERED": "1"}
    env.pop("PYTHONPATH", None)
    from auth import UsuarioRepository
    password = secrets.token_urlsafe(24)
    repo = UsuarioRepository()
    repo.adicionar_usuario("suporte.n1", password, "suporte_n1")
    users_path = output.with_suffix(".users.json")
    with users_path.open("x", encoding="utf-8") as stream:
        json.dump([asdict(u) for u in repo._usuarios.values()], stream)
    env["SIGMA_USERS_FILE"] = str(users_path)
    events = output.with_suffix(".events.jsonl")
    if events.exists():
        raise RuntimeError("Use a new output path; previous acceptance evidence is preserved")
    events.touch()
    log_path = output.with_suffix(".server.log")
    records = []
    base = f"http://127.0.0.1:{args.port}"
    commit = subprocess.check_output(["git", "-c", f"safe.directory={checkout.as_posix()}", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()

    def count():
        return sum(json.loads(line)["phase"] == "provider_called" for line in events.read_text().splitlines())

    def check(name, passed, observed):
        records.append({"name": name, "passed": bool(passed), "observed": observed})
        print(f"{'PASS' if passed else 'FAIL'}: {name}: {observed}", flush=True)

    process = None
    ready = False
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [str(interpreter), str(Path(__file__).resolve()), "--serve", "--checkout", str(checkout),
             "--port", str(args.port), "--events", str(events)], cwd=checkout, env=env,
            stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError("Acceptance server exited before becoming ready; inspect its log")
                try:
                    if request(base, "GET", "/api/status")[0] == 401:
                        ready = True
                        break
                except OSError:
                    time.sleep(0.2)
            if not ready:
                raise RuntimeError("Acceptance server did not become ready")

            status, body, _ = request(base, "POST", "/api/alertas", ALERT)
            check("token_required_before_provider", status == 401 and count() == 0, {"http": status, "provider_calls": count()})
            status, body, _ = request(base, "POST", "/api/auth/login",
                                      {"username": "suporte.n1", "password": password})
            login = json.loads(body)
            check("session_login", status == 200 and FAKE_KEY not in body and bool(login.get("access_token")), {"http": status})
            token = login["access_token"]
            auth = {"Authorization": f"Bearer {token}", "Origin": ORIGIN}
            status, _, _ = request(base, "GET", "/api/usuarios", headers=auth)
            check("rbac_insufficient_role", status == 403, {"http": status})

            status, body, headers = request(base, "POST", "/api/alertas", ALERT, auth)
            result = json.loads(body)
            check("authenticated_sanitized_success", status == 200 and set(result) == {
                "status", "dados_enviados_nuvem", "diagnostico_ia"} and result["diagnostico_ia"] == "Diagnóstico K10 simulado"
                and "192.0.2.10" not in body and "dr.joao" not in body and FAKE_KEY not in body,
                {"http": status, "contract": sorted(result)})
            check("allowed_origin_response", headers.get("access-control-allow-origin") == ORIGIN, {"http": status})

            for marker in ("K10_PROVIDER_ERROR", "K10_INVALID_JSON", "K10_TIMEOUT"):
                payload = {**ALERT, "descricao_erro": f"Falha de teste {marker}"}
                start = time.monotonic()
                status, body, _ = request(base, "POST", "/api/alertas", payload, auth)
                elapsed = time.monotonic() - start
                result = json.loads(body)
                passed = status == 200 and result.get("diagnostico_ia") == (
                    "Diagnóstico de IA indisponível no momento. Tente novamente mais tarde."
                ) and PRIVATE_DETAIL not in body and FAKE_KEY not in body
                if marker == "K10_TIMEOUT":
                    passed = passed and 14 <= elapsed <= 15 and '"provider_cancelled"' in events.read_text()
                check(marker.lower(), passed, {"http": status, "seconds": round(elapsed, 3)})

            for name, payload, origin, expected in (
                ("untrusted_origin", ALERT, "https://untrusted.example", 403),
                ("invalid_payload", {}, ORIGIN, 422),
                ("fail_closed", {**ALERT, "descricao_erro": "K10_SANITIZER_ERROR"}, ORIGIN, 500),
            ):
                before = count()
                status, body, _ = request(base, "POST", "/api/alertas", payload, {**auth, "Origin": origin})
                check(name, status == expected and count() == before and PRIVATE_DETAIL not in body,
                      {"http": status, "new_provider_calls": count() - before})

            for requested_headers, name in (("content-type", "preflight_current_contract"),
                                             ("content-type,authorization", "preflight_authenticated_browser")):
                status, _, _ = request(base, "OPTIONS", "/api/alertas", headers={
                    "Origin": ORIGIN, "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": requested_headers,
                })
                check(name, status == 200, {"http": status})
            status, _, _ = request(base, "POST", "/api/auth/logout", headers=auth)
            after, _, _ = request(base, "GET", "/api/status", headers=auth)
            check("logout_revokes_session", status == 200 and after == 401, {"logout": status, "same_token_after_logout": after})

            for missing in ("OPENROUTER_API_KEY", "SIGMA_LLM_MODEL", "SIGMA_CORS_ORIGINS", "SIGMA_JWT_SECRET", "SIGMA_USERS_FILE"):
                invalid_env = {key: value for key, value in env.items() if key != missing}
                imported = subprocess.run([str(interpreter), "-c", "import sys; sys.path.insert(0, 'backend'); import main"], cwd=checkout,
                                          env=invalid_env, capture_output=True, text=True, timeout=15)
                check(f"startup_requires_{missing.lower()}", imported.returncode != 0 and missing in imported.stderr
                      and FAKE_KEY not in imported.stderr, {"exit_code": imported.returncode})
            log.flush()
            logged = log_path.read_text(encoding="utf-8")
            check("safe_server_logs", all(value not in logged for value in (PRIVATE_DETAIL, FAKE_KEY, token)),
                  {"private_values_in_log": any(value in logged for value in (PRIVATE_DETAIL, FAKE_KEY, token))})
        finally:
            if process and not (args.keep_server and ready):
                process.terminate()
                process.wait(timeout=15)
            report = {"checkout_commit": commit, "transport": "real HTTP over loopback / Uvicorn",
                      "provider": "httpx2.MockTransport; no real AI provider called", "results": records,
                      "passed": sum(r["passed"] for r in records), "failed": sum(not r["passed"] for r in records),
                      "server_pid": process.pid if args.keep_server and ready else None}
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            if args.keep_server and ready:
                output.with_suffix(".browser.json").write_text(json.dumps({
                    "username": "suporte.n1", "password": password, "api_url": base,
                    "server_pid": process.pid,
                }), encoding="utf-8")
    return 1 if any(not item["passed"] for item in records) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("test-results/k10-acceptance.json"))
    parser.add_argument("--port", type=int, default=18000)
    parser.add_argument("--keep-server", action="store_true")
    parser.add_argument("--serve", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--events", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.serve:
        serve(args.checkout.resolve(), args.port, args.events)
        return 0
    return validate(args)


if __name__ == "__main__":
    raise SystemExit(main())
