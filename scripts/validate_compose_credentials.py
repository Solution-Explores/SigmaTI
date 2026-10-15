"""Valida a K03 usando somente `docker compose config`, sem tocar no Engine."""

import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "ZABBIX_DB_USER",
    "ZABBIX_DB_PASS",
    "GF_SECURITY_ADMIN_USER",
    "GF_SECURITY_ADMIN_PASSWORD",
)
PASSWORDS = ("POSTGRES_PASSWORD", "ZABBIX_DB_PASS", "GF_SECURITY_ADMIN_PASSWORD")
LEGACY = ("N8N_USER", "N8N_PASS", "N8N_BASIC_AUTH_ACTIVE", "N8N_BASIC_AUTH_USER", "N8N_BASIC_AUTH_PASSWORD")


class ValidationError(RuntimeError):
    """Mensagens do validador descrevem verificações, nunca seus valores."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


class CredentialChecks:
    def __init__(self) -> None:
        self.count = 0
        # Não herdar credenciais reais nem controles Compose do ambiente local.
        self.clean_env = {
            name: value for name, value in os.environ.items()
            if name not in (*REQUIRED, *LEGACY, "POSTGRES_DB", "N8N_BIND_IP", "GRAFANA_BIND_IP")
            and not name.startswith("COMPOSE_")
        }
        self.clean_env["COMPOSE_ANSI"] = "never"
        self.values = {
            name: secrets.token_hex(32) if name in PASSWORDS else "test_" + secrets.token_hex(6)
            for name in REQUIRED
        }
        self.valid_env = {
            **self.clean_env, **self.values, "POSTGRES_DB": "sigma_config_test",
            "N8N_BIND_IP": "127.0.0.1", "GRAFANA_BIND_IP": "127.0.0.1",
        }

    def passed(self, label: str) -> None:
        self.count += 1
        print(f"PASS: {label}")

    def compose(self, env_file: Path, env: dict[str, str], profile: str | None = None,
                *, render: bool = False) -> subprocess.CompletedProcess:
        command = [
            "docker", "compose", "--project-name", "sigma-k03-validation",
            "--project-directory", str(ROOT), "-f", str(ROOT / "docker-compose.yml"),
            "--env-file", str(env_file),
        ]
        if profile:
            command += ["--profile", profile]
        command += ["config", "--format", "json"] if render else ["config", "--quiet"]
        # Nunca imprimir stdout/stderr: a configuração renderizada contém senhas.
        return subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                              encoding="utf-8", errors="replace", timeout=30)

    def check_template(self) -> None:
        entries = {}
        for line in (ROOT / ".env.example").read_text(encoding="utf-8-sig").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                name, separator, value = line.partition("=")
                if separator:
                    require(name.strip() not in entries, "Variável duplicada no template.")
                    entries[name.strip()] = value.strip()
        require(all(name in entries and entries[name] == "" for name in REQUIRED),
                "O template deve conter as seis credenciais obrigatórias vazias.")
        require(not any(name in entries for name in LEGACY), "Configuração n8n obsoleta no template.")
        source = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        for name in REQUIRED:
            references = re.findall(r"\${" + re.escape(name) + r"([^}]*)}", source)
            require(bool(references) and all(ref.startswith(":?") and len(ref) > 2 for ref in references),
                    f"{name} deve ser obrigatório e não pode ter fallback no Compose.")
        self.passed("template vazio e seis credenciais obrigatórias sem fallback")

    def check_gitignore(self) -> None:
        result = subprocess.run(["git", "check-ignore", "--quiet", ".env"], cwd=ROOT,
                                env=self.clean_env, capture_output=True, timeout=10)
        require(result.returncode == 0, "O .env deve estar ignorado pelo Git.")
        self.passed(".env ignorado pelo Git")

    def expect_success(self, env_file: Path, label: str, profile: str | None = None) -> None:
        result = self.compose(env_file, self.valid_env, profile)
        require(result.returncode == 0, f"Configuração recusada: {label}.")
        require(not result.stderr.strip(), f"Aviso inesperado: {label}.")
        require(not result.stdout.strip(), f"Saída inesperada: {label}.")
        self.passed(label)

    def check_rendered_values(self, env_file: Path, profile: str | None = None) -> None:
        result = self.compose(env_file, self.valid_env, profile, render=True)
        require(result.returncode == 0, "Falha ao renderizar a configuração para inspeção.")
        # Não deixar o parser refletir o JSON em uma exceção.
        try:
            services = json.loads(result.stdout)["services"]
        except (ValueError, KeyError, TypeError):
            raise ValidationError("Configuração renderizada inválida.") from None
        expected = {"db", "n8n"}
        if profile:
            expected |= {"postgres-server", "zabbix-server", "grafana"}
        require(set(services) == expected, "Serviços inesperados no perfil validado.")
        db = services["db"]["environment"]
        require(db.get("POSTGRES_USER") == self.values["POSTGRES_USER"] and
                db.get("POSTGRES_PASSWORD") == self.values["POSTGRES_PASSWORD"],
                "O banco principal deve consumir as credenciais do ambiente.")
        n8n = services["n8n"].get("environment") or {}
        require(not any(name in n8n for name in LEGACY), "O n8n não deve receber Basic Auth legado.")
        if profile:
            for service in ("postgres-server", "zabbix-server"):
                env = services[service]["environment"]
                require(env.get("POSTGRES_USER") == self.values["ZABBIX_DB_USER"] and
                        env.get("POSTGRES_PASSWORD") == self.values["ZABBIX_DB_PASS"],
                        "Banco e servidor Zabbix devem usar as mesmas credenciais externas.")
            grafana = services["grafana"]["environment"]
            require(all(grafana.get(name) == self.values[name]
                        for name in ("GF_SECURITY_ADMIN_USER", "GF_SECURITY_ADMIN_PASSWORD")),
                    "O Grafana deve consumir suas credenciais iniciais do ambiente.")
        self.passed(f"credenciais e serviços renderizados: {profile or 'padrão'}")

    def expect_rejection(self, env_file: Path, env: dict[str, str], label: str,
                         profile: str | None = None, variable: str | None = None) -> None:
        result = self.compose(env_file, env, profile)
        require(result.returncode != 0, f"A configuração deveria falhar: {label}.")
        if variable:
            require(variable in result.stderr, f"A rejeição deve identificar {variable}.")
        require(not any(self.values[name] in result.stdout + result.stderr for name in PASSWORDS),
                "Uma rejeição não deve expor valores de senhas.")
        self.passed(label)

    def run(self) -> None:
        self.check_template()
        self.check_gitignore()
        with tempfile.TemporaryDirectory(prefix="sigma-k03-") as directory:
            # Arquivo vazio impede qualquer leitura implícita do .env do usuário.
            empty_env = Path(directory) / "empty.env"
            empty_env.write_text("", encoding="utf-8")
            self.expect_success(empty_env, "Compose padrão com credenciais temporárias")
            self.expect_success(empty_env, "Compose monitoring com credenciais temporárias", "monitoring")
            self.expect_success(ROOT / ".env.example", "template preenchido pelo ambiente", "monitoring")
            self.check_rendered_values(empty_env)
            self.check_rendered_values(empty_env, "monitoring")
            self.expect_rejection(ROOT / ".env.example", self.clean_env,
                                  "template sem preenchimento recusado")
            for profile in (None, "monitoring"):
                for variable in REQUIRED:
                    for state in ("ausente", "vazia"):
                        env = self.valid_env.copy()
                        if state == "ausente":
                            env.pop(variable)
                        else:
                            env[variable] = ""
                        self.expect_rejection(empty_env, env,
                                              f"{profile or 'padrão'} recusa {variable} {state}",
                                              profile, variable)
        print(f"Resultado: {self.count} verificações aprovadas; nenhum contêiner iniciado.")


def main() -> int:
    try:
        CredentialChecks().run()
    except ValidationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    except (OSError, subprocess.SubprocessError):
        print("FAIL: confira Python, Git, Docker Compose e o acesso a arquivos temporários.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
