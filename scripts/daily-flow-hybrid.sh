#!/bin/bash
# Flujo diario con verificación de PC local (para VPS)
# Si la PC local está disponible, no ejecuta aquí

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Cargar variables de entorno
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Verificar si PC local está disponible
echo "🔍 Verificando disponibilidad de PC local..."
python3 scripts/check-pc-available.py

if [ $? -eq 0 ]; then
    echo "✅ PC local está disponible"
    echo "   No ejecutando en VPS (PC local lo hará)"
    exit 0
fi

echo "⚠️  PC local NO está disponible"
echo "   Ejecutando en VPS (fallback)..."
echo ""

# Ejecutar flujo normal
bash scripts/daily-flow.sh

