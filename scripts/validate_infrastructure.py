"""K04: conferir portas e imagens; opcionalmente consultar manifests oficiais."""

import argparse
import hashlib
from ipaddress import ip_address
import json
import re
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from .validate_compose_credentials import ROOT, CredentialChecks, ValidationError, require
except ImportError:
    from validate_compose_credentials import ROOT, CredentialChecks, ValidationError, require


PORTS = {"n8n": 5678, "grafana": 3000, "zabbix-server": 10051}
BINDS = {"n8n": "N8N_BIND_IP", "grafana": "GRAFANA_BIND_IP", "zabbix-server": "ZABBIX_BIND_IP"}
PUBLISHERS = {
    "postgres": ("library/postgres", r"15\.\d+-alpine\d+\.\d+", {"db", "postgres-server"}),
    "n8nio/n8n": ("n8nio/n8n", r"1\.\d+\.\d+", {"n8n"}),
    "zabbix/zabbix-server-pgsql": ("zabbix/zabbix-server-pgsql", r"alpine-6\.4\.\d+", {"zabbix-server"}),
    "grafana/grafana": ("grafana/grafana", r"10\.\d+\.\d+", {"grafana"}),
}
ACCEPT = ", ".join(("application/vnd.oci.image.index.v1+json",
                    "application/vnd.docker.distribution.manifest.list.v2+json",
                    "application/vnd.oci.image.manifest.v1+json",
                    "application/vnd.docker.distribution.manifest.v2+json"))


def image_map(lock: dict) -> dict[str, str]:
    require(lock.get("schema_version") == 1, "Formato de lock desconhecido.")
    entries = lock.get("images", [])
    require(len(entries) == len(PUBLISHERS), "O lock deve conter as quatro imagens oficiais.")
    result, seen = {}, set()
    for entry in entries:
        repository = entry.get("repository", "")
        require(repository in PUBLISHERS and repository not in seen, "Publicador inesperado ou duplicado.")
        seen.add(repository)
        registry_repo, pattern, services = PUBLISHERS[repository]
        require(entry.get("registry_repository") == registry_repo, "Repositório oficial inconsistente.")
        require(bool(re.fullmatch(pattern, entry.get("tag", ""))), "A imagem deve usar release explícita da linha aprovada.")
        require(bool(re.fullmatch(r"sha256:[0-9a-f]{64}", entry.get("digest", ""))), "Digest SHA-256 inválido.")
        require(set(entry.get("services", [])) == services, "Mapeamento de serviços inconsistente.")
        reference = f"{repository}:{entry['tag']}@{entry['digest']}"
        for service in services:
            result[service] = reference
    return result


def validate_model(model: dict, images: dict[str, str], bindings: dict[str, str]) -> None:
    services = model["services"]
    require(set(services) in ({"db", "n8n"}, set(images)), "Serviços inesperados na configuração.")
    for name, service in services.items():
        require(service.get("image") == images[name], f"Imagem de {name} difere do lock aprovado.")
        require(not service.get("network_mode") == "host", "Rede host não faz parte da política.")
        ports = service.get("ports") or []
        if name not in PORTS:
            require(not ports, "Os bancos não podem publicar portas no host.")
            continue
        require(len(ports) == 1, f"Publicações inesperadas em {name}.")
        port = ports[0]
        require(port.get("target") == PORTS[name] and str(port.get("published")) == str(PORTS[name])
                and port.get("protocol") == "tcp", f"Porta ou protocolo inesperado em {name}.")
        try:
            address = ip_address(port.get("host_ip", ""))
            expected = ip_address(bindings[name])
        except ValueError:
            raise ValidationError(f"Defina um IP explícito para {name}.") from None
        effective = getattr(address, "ipv4_mapped", None) or address
        require(not effective.is_unspecified and not effective.is_multicast, f"Bind amplo ou multicast recusado em {name}.")
        require(address == expected, f"O bind de {name} não corresponde ao ambiente validado.")


def render(checks: CredentialChecks, env: dict[str, str], profile: str | None = "monitoring") -> dict:
    result = checks.compose(ROOT / ".env.example", env, profile, render=True)
    require(result.returncode == 0, "Falha ao renderizar a configuração K04.")
    try:
        return json.loads(result.stdout)
    except ValueError:
        raise ValidationError("Configuração K04 inválida.") from None


def verify_registry(lock: dict) -> None:
    # Somente endpoints de metadados fixos do registro oficial; não buscar camadas.
    for entry in lock["images"]:
        repository = entry["registry_repository"]
        query = urlencode({"service": "registry.docker.io", "scope": f"repository:{repository}:pull"})
        with urlopen("https://auth.docker.io/token?" + query, timeout=30) as response:
            token = json.load(response)["token"]
        headers = {"Authorization": "Bearer " + token, "Accept": ACCEPT}
        for reference in (entry["tag"], entry["digest"]):
            request = Request(f"https://registry-1.docker.io/v2/{repository}/manifests/{reference}", headers=headers)
            with urlopen(request, timeout=30) as response:
                body = response.read()
                digest = "sha256:" + hashlib.sha256(body).hexdigest()
                require(response.headers.get("Docker-Content-Digest") == digest == entry["digest"],
                        f"Manifest de {repository} diverge do lock; revisar sem atualizar automaticamente.")
            manifest = json.loads(body)
            platforms = {(m.get("platform", {}).get("os"), m.get("platform", {}).get("architecture"))
                         for m in manifest.get("manifests", [])}
            require({("linux", "amd64"), ("linux", "arm64")} <= platforms,
                    f"Plataformas Linux amd64/arm64 não confirmadas em {repository}.")
        print(f"PASS: registro oficial confirma {entry['repository']}:{entry['tag']} e digest")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-registry", action="store_true", help="Consultar somente manifests públicos do Docker Hub")
    options = parser.parse_args()
    try:
        lock = json.loads((ROOT / "docker-images.lock.json").read_text(encoding="utf-8"))
        images = image_map(lock)
        checks = CredentialChecks()
        for label, address in (("padrão", "127.0.0.1"), ("loopback IPv6", "::1"),
                               ("IP de gerência fictício", "192.0.2.10")):
            env = checks.valid_env.copy()
            env.update({variable: address for variable in BINDS.values()})
            for profile in (None, "monitoring"):
                validate_model(render(checks, env, profile), images, {name: address for name in BINDS})
                print(f"PASS: portas, bancos e imagens: {label}, perfil {profile or 'padrão'}")
        # Recusar as duas famílias de bind amplo, sem iniciar serviços.
        for name, variable in BINDS.items():
            for address in ("0.0.0.0", "::"):
                env = checks.valid_env.copy()
                env[variable] = address
                model = render(checks, env)
                try:
                    validate_model(model, images,
                                   {service: env[key] for service, key in BINDS.items()})
                except ValidationError:
                    print(f"PASS: política recusa bind amplo em {name}")
                else:
                    raise ValidationError(f"A política deveria recusar bind amplo em {name}.")
        if options.verify_registry:
            verify_registry(lock)
        print("K04: configuração aprovada; nenhum contêiner iniciado e nenhuma camada baixada.")
    except ValidationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, HTTPError, URLError, subprocess.SubprocessError):
        print("FAIL: confira o lock, o Docker Compose e o acesso aos metadados oficiais; nenhum valor de credencial foi registrado.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
