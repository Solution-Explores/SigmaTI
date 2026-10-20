#!/usr/bin/env bash
# Instala API/coleta ativa no checkout. Não instala serviços nem captura pacotes.
set -euo pipefail
umask 077
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
: "${SIGMA_DATABASE_URL:?Exporte a URL do PostgreSQL já inicializado}"
python3 -c 'import sys; assert sys.version_info >= (3,12), "Python 3.12+ obrigatório"'
[[ -x .venv/bin/python ]] || python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m alembic upgrade head
printf '%s\n' 'API/coleta instalada e migrada. Cadastre o gestor e siga doc/backup-restauracao.md.'
