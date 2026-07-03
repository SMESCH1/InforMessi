#!/usr/bin/env bash
# Regenera los reports base de julio 2026 (2026-07-03 a 2026-07-19) con el
# pipeline arreglado y corre el baseline de evals (checks + judge LLM).
#
# Requiere GROQ_API_KEY (en el entorno o en el .env de la raíz del repo).
# Pensado para correrse una vez que la key esté disponible (usuario o CI):
#   bash scripts/regenerate-base-reports.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# --- Check de GROQ_API_KEY (entorno o .env de la raíz) ---
if [ -z "${GROQ_API_KEY:-}" ] && ! grep -qs "^GROQ_API_KEY=." .env; then
    echo "ERROR: GROQ_API_KEY no está disponible." >&2
    echo "Definila en el entorno (export GROQ_API_KEY=...) o agregala al .env" >&2
    echo "de la raíz del repo (GROQ_API_KEY=...). Sin la key no se puede" >&2
    echo "regenerar los reports base ni correr el judge de evals." >&2
    exit 1
fi

echo "==> Regenerando reports base 2026-07-03 a 2026-07-19 (provider: groq)"
python scripts/generate-advance-reports.py \
    --start-date 2026-07-03 \
    --end-date 2026-07-19 \
    --overwrite \
    --provider groq

echo ""
echo "==> Corriendo baseline de evals (checks + judge LLM)"
python evals/run_evals.py --range 2026-07-03:2026-07-19 --judge

echo ""
echo "==> Listo. Revisá data/eval-history.json y commiteá reports/ + eval-history."
