#!/bin/bash
# Script para iniciar el servidor webhook de InforMessi
# InforMessi - Automatización

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Activar venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Entorno virtual no encontrado"
    exit 1
fi

echo -e "${BLUE}🚀 Iniciando servidor webhook de InforMessi${NC}"
echo "=========================================="
echo ""
echo "🌐 El servidor estará disponible en:"
echo "   http://localhost:8000"
echo ""
echo "💡 Para detener: Ctrl+C"
echo ""

# Ejecutar servidor
python3 scripts/webhook-server.py

