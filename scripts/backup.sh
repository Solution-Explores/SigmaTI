#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec "${SIGMA_PYTHON:-$ROOT/.venv/bin/python}" "$ROOT/scripts/recovery.py" backup "$@"
