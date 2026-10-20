#!/usr/bin/env bash
# Atualização deliberada com backup offline, sem reset, force-push ou remoção de volumes.
set -euo pipefail
umask 077
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[[ $# == 2 && "$1" =~ ^[0-9a-f]{40}$ ]] || { echo 'Uso: bash scripts/update.sh SHA_APROVADO PASTA_BACKUP_NOVA' >&2; exit 2; }
[[ -z "$(git status --porcelain)" ]] || { echo 'Checkout com alterações; atualização recusada.' >&2; exit 1; }
: "${SIGMA_DB_CONTAINER:?Informe o contêiner PostgreSQL}"
: "${SIGMA_AUDIT_PATH:?Informe a trilha JSONL}"
: "${SIGMA_WRITERS_STOPPED:?Pare TODOS os escritores e exporte SIGMA_WRITERS_STOPPED=1}"
[[ "$SIGMA_WRITERS_STOPPED" == 1 ]] || exit 1
if command -v systemctl >/dev/null && systemctl is-active --quiet sigma-coleta.service; then
  echo 'sigma-coleta.service ainda está ativo; pare-o antes do backup.' >&2
  exit 1
fi
git fetch origin
git merge-base --is-ancestor HEAD "$1"
bash scripts/backup.sh --container "$SIGMA_DB_CONTAINER" --audit "$SIGMA_AUDIT_PATH" --bundle "$2" --quiesced
git merge --ff-only "$1"
bash scripts/install.sh
printf '%s\n' 'Atualizado. Mantenha offline até validar; reinício e eventual restauração são deliberados, veja o guia.'
