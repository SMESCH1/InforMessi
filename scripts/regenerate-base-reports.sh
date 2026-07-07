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

# Forzar el modelo de Groq: el .env local puede tener LLM_MODEL apuntando a un
# modelo de Ollama (ej. llama3.2), que Groq rechaza con 404 model_not_found.
export LLM_PROVIDER=groq
export LLM_MODEL=llama-3.3-70b-versatile

# Rango parametrizable: por defecto arranca MAÑANA (hora argentina) para no
# pisar reports de días ya publicados. Uso: bash scripts/regenerate-base-reports.sh [START] [END]
START_DATE="${1:-$(python -c "import sys; sys.path.insert(0,'scripts'); from time_utils import now_ar; from datetime import timedelta; print((now_ar()+timedelta(days=1)).strftime('%Y-%m-%d'))")}"
END_DATE="${2:-2026-07-19}"

echo "==> Regenerando reports base ${START_DATE} a ${END_DATE} (provider: groq, model: ${LLM_MODEL})"
python scripts/generate-advance-reports.py \
    --start-date "${START_DATE}" \
    --end-date "${END_DATE}" \
    --overwrite \
    --provider groq

echo ""
echo "==> Corriendo baseline de evals (checks + judge LLM)"
python evals/run_evals.py --range "${START_DATE}:${END_DATE}" --judge

echo ""
echo "==> Listo. Revisá data/eval-history.json y commiteá reports/ + eval-history."
