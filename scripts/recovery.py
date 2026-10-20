"""Backup/restauração offline do PostgreSQL Docker e da trilha JSONL do SIGMA."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sigma_eng.audit_chain import AuditChain


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def key():
    value = os.environ.get("SIGMA_AUDIT_KEY", "").encode()
    if len(value) < 32:
        raise ValueError("SIGMA_AUDIT_KEY deve conter pelo menos 32 bytes e ser fornecida fora do pacote.")
    return value


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def docker(container, command, *, source=None, destination=None):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", container):
        raise ValueError("Identificador de contêiner inválido.")
    # Comando shell é constante; nomes e senhas nunca são interpolados pelo host.
    result = subprocess.run(["docker", "exec", "-i", container, "sh", "-ec", command],
        stdin=source, stdout=destination or subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
    if result.returncode:
        raise RuntimeError("Ferramenta PostgreSQL falhou; nenhuma saída privada foi publicada.")
    return result.stdout


def sql(container, statement):
    # subprocess exige descritor real, e não BytesIO.
    with tempfile.TemporaryFile() as stream:
        stream.write(statement.encode()); stream.seek(0)
        return docker(container, 'export PGOPTIONS="-c timezone=UTC -c datestyle=ISO"; exec psql -X -v ON_ERROR_STOP=1 -At -U "$POSTGRES_USER" -d "$POSTGRES_DB"', source=stream).decode().strip()


def fingerprint(container):
    tables = sql(container, "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;").splitlines()
    result = {}
    for table in tables:
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z_0-9]*", table):
            raise ValueError("Nome de tabela fora do contrato SIGMA.")
        rows = sql(container, f'SELECT row_to_json(t)::text FROM public."{table}" t ORDER BY row_to_json(t)::text;')
        result[table] = {"sha256": hashlib.sha256(rows.encode()).hexdigest(),
                         "rows": int(sql(container, f'SELECT count(*) FROM public."{table}";'))}
    return result


def audit(path, secret):
    chain = AuditChain(path, chave=secret)
    if not Path(path).is_file() or not chain.verificar()[0]:
        raise ValueError("Trilha de auditoria ausente ou inválida.")
    return len(chain)


def verify(bundle):
    bundle = Path(bundle)
    secret = key()
    for name in ("manifest.json", "database.dump", "audit.jsonl"):
        p = bundle / name
        if p.is_symlink() or not p.is_file():
            raise ValueError("Pacote incompleto ou com link simbólico.")
    signed = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    manifest = signed["manifest"]
    expected = hmac.new(secret, canonical(manifest), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signed["hmac_sha256"]):
        raise ValueError("Manifesto não autenticado; chave errada ou pacote alterado.")
    if manifest["format"] != 1:
        raise ValueError("Formato de backup incompatível.")
    for name in ("database.dump", "audit.jsonl"):
        if digest(bundle/name) != manifest["files"][name]:
            raise ValueError("Checksum de backup inválido.")
    if audit(bundle/"audit.jsonl", secret) != manifest["audit_entries"]:
        raise ValueError("Contagem de auditoria divergente.")
    return manifest


def backup(container, audit_path, output, *, quiesced=False):
    if not quiesced:
        raise ValueError("Pare API, sonda e demais escritores; confirme com --quiesced.")
    secret = key()
    output = Path(output).absolute()
    if output.exists():
        raise ValueError("Destino do pacote já existe.")
    output.parent.mkdir(parents=True, exist_ok=True)
    before = digest(audit_path)
    entries = audit(audit_path, secret)
    initial_tables = fingerprint(container)
    with tempfile.TemporaryDirectory(prefix=".sigma-backup-", dir=output.parent) as temporary:
        stage = Path(temporary)
        os.chmod(stage, 0o700)
        dump = stage/"database.dump"
        with dump.open("xb") as stream:
            os.chmod(dump, 0o600)
            docker(container, 'exec pg_dump -Fc --no-owner --no-privileges -U "$POSTGRES_USER" -d "$POSTGRES_DB"', destination=stream)
        shutil.copyfile(audit_path, stage/"audit.jsonl")
        os.chmod(stage/"audit.jsonl", 0o600)
        manifest = {"format": 1, "created_at": datetime.now(timezone.utc).isoformat(),
            "postgres_major": int(sql(container, "SHOW server_version_num;"))//10000,
            "audit_entries": entries, "tables": fingerprint(container),
            "files": {name: digest(stage/name) for name in ("database.dump", "audit.jsonl")}}
        if manifest["tables"] != initial_tables:
            raise ValueError("Banco mudou durante backup; interrompa escritores e repita.")
        if digest(audit_path) != before or digest(stage/"audit.jsonl") != before:
            raise ValueError("Auditoria mudou durante backup; interrompa escritores e repita.")
        # O inventário confere o banco quiescente, além do snapshot consistente do pg_dump.
        signed = {"manifest": manifest, "hmac_sha256": hmac.new(secret, canonical(manifest), hashlib.sha256).hexdigest()}
        m = stage/"manifest.json"
        m.write_bytes(canonical(signed)); os.chmod(m, 0o600)
        verify(stage)
        # Reserva exclusiva evita substituir um destino criado por outro processo.
        output.mkdir(mode=0o700)
        try:
            for name in ("database.dump", "audit.jsonl", "manifest.json"):
                os.replace(stage/name, output/name)
        except BaseException:
            shutil.rmtree(output)
            raise
    return manifest


def restore(container, bundle, audit_output, *, quiesced=False):
    if not quiesced:
        raise ValueError("Destino deve estar offline; confirme com --quiesced.")
    manifest = verify(bundle)
    output = Path(audit_output).absolute()
    if output.exists():
        raise ValueError("Destino da auditoria já existe; não será sobrescrito.")
    if int(sql(container, "SHOW server_version_num;"))//10000 != manifest["postgres_major"]:
        raise ValueError("Ensaio exige a mesma versão principal PostgreSQL.")
    objects = sql(container, "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%' AND n.nspname NOT LIKE 'pg_temp%';")
    if int(objects):
        raise ValueError("Banco destino não está vazio; restauração recusada.")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Reserva da trilha antes de tocar no banco; falhas não publicam trilha válida.
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as trail, (Path(bundle)/"database.dump").open("rb") as dump:
            docker(container, 'exec pg_restore --exit-on-error --single-transaction --no-owner --no-privileges -U "$POSTGRES_USER" -d "$POSTGRES_DB"', source=dump)
            if fingerprint(container) != manifest["tables"]:
                raise ValueError("Banco restaurado diverge do inventário; mantenha offline e descarte o destino de ensaio.")
            with (Path(bundle)/"audit.jsonl").open("rb") as source:
                shutil.copyfileobj(source, trail)
            trail.flush(); os.fsync(trail.fileno())
        audit(output, key())
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    for action in ("backup", "restore", "verify"):
        p = commands.add_parser(action)
        p.add_argument("--bundle", type=Path, required=True)
        if action != "verify":
            p.add_argument("--container", required=True)
            p.add_argument("--audit", type=Path, required=True)
            p.add_argument("--quiesced", action="store_true")
    args = parser.parse_args()
    try:
        if args.action == "backup": result = backup(args.container, args.audit, args.bundle, quiesced=args.quiesced)
        elif args.action == "restore": result = restore(args.container, args.bundle, args.audit, quiesced=args.quiesced)
        else: result = verify(args.bundle)
        print(json.dumps({"status": "ok", "tables": len(result["tables"]), "audit_entries": result["audit_entries"]}))
    except (ValueError, RuntimeError, OSError, KeyError, TypeError, subprocess.SubprocessError):
        print("Recuperação falhou; confira pacote, chave, escritores parados e destino vazio.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
