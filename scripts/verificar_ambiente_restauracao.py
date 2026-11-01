"""Confere se uma máquina está pronta para a restauração da #25 (guia backup-restauracao.md).

Só biblioteca padrão: roda antes de existir o venv, no Windows ou no Linux.
Não imprime chave, senha nem conteúdo do pacote. Saída 0 só se tudo passar.

Uso (da raiz do clone):
  python scripts/verificar_ambiente_restauracao.py --sha <SHA> --imagem <IMAGEM@sha256:...> [--bundle PASTA]
"""
import argparse
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
resultados = []


def registrar(nome, passou, dica=""):
    resultados.append(passou)
    print(("OK    " if passou else "FALTA ") + nome + ("" if passou or not dica else f"  -> {dica}"))


def executa(*comando, cwd=None, timeout=60):
    try:
        done = subprocess.run(comando, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return done.returncode, done.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def alcanca(host, porta=443):
    try:
        with socket.create_connection((host, porta), timeout=5):
            return True
    except OSError:
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sha", required=True, help="SHA completo do código aprovado")
    parser.add_argument("--imagem", required=True, help="Imagem do PostgreSQL com digest (do report.json)")
    parser.add_argument("--porta", type=int, default=55432, help="Porta local do PostgreSQL de destino")
    parser.add_argument("--bundle", type=Path, help="Pasta do pacote (database.dump, audit.jsonl, manifest.json)")
    args = parser.parse_args()

    registrar("Python 3.12 ou superior", sys.version_info >= (3, 12), f"encontrado {sys.version.split()[0]}")
    registrar("git instalado", shutil.which("git") is not None, "instalar o Git")
    code, head = executa("git", "rev-parse", "HEAD", cwd=ROOT)
    registrar(f"Clone no SHA {args.sha[:10]}", code == 0 and head == args.sha, "git checkout <SHA>")
    code, mudancas = executa("git", "diff", "--name-only", "HEAD", cwd=ROOT)
    registrar("Clone sem alterações em arquivos rastreados", code == 0 and not mudancas, "descartar alterações locais")

    registrar("Docker (CLI)", shutil.which("docker") is not None, "instalar Docker; sem ele não há restauração")
    code, _ = executa("docker", "info")
    registrar("Docker em execução (daemon responde)", code == 0, "iniciar o Docker Desktop/serviço")
    code, _ = executa("docker", "compose", "version")
    registrar("docker compose (plugin v2)", code == 0, "instalar o plugin do Compose")
    digest = args.imagem.rsplit("@", 1)[-1]
    code, digests = executa("docker", "image", "inspect", args.imagem, "--format", "{{json .RepoDigests}}")
    registrar("Imagem do PostgreSQL local, com o digest exigido", code == 0 and digest in digests,
              f"docker pull {args.imagem}")
    with socket.socket() as probe:
        livre = probe.connect_ex(("127.0.0.1", args.porta)) != 0
    registrar(f"Porta {args.porta} livre em 127.0.0.1", livre, "escolher outra com --porta")

    registrar("Espaço livre: pelo menos 2 GiB", shutil.disk_usage(ROOT).free >= 2 * 1024 ** 3, "liberar disco")
    registrar("Rede: PyPI acessível (pip)", alcanca("pypi.org"), "proxy corporativo? pedir à TI ou usar plano B")
    registrar("Rede: Docker Hub acessível (pull)", alcanca("registry-1.docker.io"), "idem")

    venv_python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_python.exists():
        code, _ = executa(str(venv_python), "-c", "import fastapi, sqlalchemy, psycopg, pytest")
        registrar("venv com as dependências (fastapi, sqlalchemy, psycopg, pytest)", code == 0,
                  "pip install -r requirements-dev.txt")
    else:
        registrar("venv criado (.venv)", False, "python -m venv .venv e pip install -r requirements-dev.txt")

    if args.bundle:
        faltando = [n for n in ("database.dump", "audit.jsonl", "manifest.json") if not (args.bundle / n).is_file()]
        registrar("Pacote com database.dump, audit.jsonl e manifest.json", not faltando, f"faltam: {', '.join(faltando)}")
        registrar("Chave fora do pacote (sem audit-key.txt dentro dele)", not (args.bundle / "audit-key.txt").exists(),
                  "mover a chave para outro canal")
    registrar("SIGMA_AUDIT_KEY definida na sessão (ao menos 32 bytes)", len(os.environ.get("SIGMA_AUDIT_KEY", "")) >= 32,
              "definir a variável com a chave recebida por canal separado")

    if not all(resultados):
        print(f"Ambiente INCOMPLETO: {resultados.count(False)} item(ns). Não restaure ainda.")
        return 1
    print("Ambiente completo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
