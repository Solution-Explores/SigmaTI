"""Cria PostgreSQL descartável; executa migrações/testes; remove apenas seu contêiner."""
import json
import argparse
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

IMAGE = "postgres:15.19-alpine3.24@sha256:f7d23353e1b15400d22ebe31189f4d314b87a4c129cc400c8c2d8d4ca127bf81"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default=IMAGE, help="Imagem explícita para ensaio adicional; CI usa o digest PostgreSQL 15.")
    parser.add_argument("--tests", default="tests engenharia/tests")
    args = parser.parse_args()
    image = args.image
    name = "sigma-identity-test-" + secrets.token_hex(6)
    password = secrets.token_hex(24)
    evidence = Path("test-results")
    evidence.mkdir(exist_ok=True)
    env_file = evidence / (name + ".env")
    env_file.write_text("POSTGRES_USER=sigma_test\nPOSTGRES_DB=sigma_test\nPOSTGRES_PASSWORD=" + password + "\n")
    try:
        subprocess.run(["docker", "run", "--detach", "--name", name, "--label", "sigmati.test=identity",
                        "--env-file", str(env_file), "--publish", "127.0.0.1::5432", image],
                       check=True, stdout=subprocess.DEVNULL)
        for _ in range(60):
            ready = subprocess.run(["docker", "exec", name, "pg_isready", "-U", "sigma_test", "-d", "sigma_test"],
                                   capture_output=True)
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("PostgreSQL de teste não ficou pronto.")
        port = subprocess.check_output(["docker", "port", name, "5432/tcp"], text=True).strip().rsplit(":", 1)[1]
        env = dict(os.environ, SIGMA_TEST_DATABASE_URL=f"postgresql+psycopg://sigma_test:{password}@127.0.0.1:{port}/sigma_test")
        env.pop("SIGMA_DATABASE_URL", None)
        command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                   "--junitxml=test-results/postgres-regression.xml"]
        command.extend(args.tests.split())
        result = subprocess.run(command, env=env)
        (evidence / "postgres-run.json").write_text(json.dumps({"image": image, "exit_code": result.returncode,
            "tests": args.tests}, indent=2))
        return result.returncode
    finally:
        env_file.unlink(missing_ok=True)
        subprocess.run(["docker", "rm", "--force", "--volumes", name], capture_output=True)


if __name__ == "__main__":
    raise SystemExit(main())
