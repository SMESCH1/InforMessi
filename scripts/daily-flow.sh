#!/bin/bash
# Flujo diario completo de InforMessi
# Actualiza el informe del día y lo envía a Telegram
# MVP - Generación Anticipada

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Colores y configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Activar venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Entorno virtual no encontrado. Ejecuta: bash setup-venv.sh"
    exit 1
fi

# Cargar variables de entorno
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
else
    echo "⚠️  Archivo .env no encontrado"
fi

# Fecha del día
DATE=$(date +"%Y-%m-%d")

echo -e "${BLUE}🚀 InforMessi - Actualización Diaria${NC}"
echo "================================================"
echo ""

# Paso 1: Actualizar informe del día
echo -e "${BLUE}🔄 Paso 1: Actualizando informe del día...${NC}"
python3 scripts/update-today-report.py --date "$DATE" 2>&1 | tail -10

if [ $? -ne 0 ]; then
    echo "❌ Error al actualizar informe"
    exit 1
fi

echo ""
echo -e "${BLUE}📤 Paso 2: Enviando informe a chat de revisión...${NC}"

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_PREVIEW_CHAT_ID" ]; then
    echo -e "${YELLOW}⚠️  Variables de Telegram no configuradas${NC}"
    echo "   Informe actualizado en: reports/${DATE}.json"
    echo "   Configura TELEGRAM_BOT_TOKEN y TELEGRAM_PREVIEW_CHAT_ID en .env"
    exit 0
fi

python3 scripts/send-daily-report-review.py --date "$DATE" 2>&1 | tail -10

echo ""
echo "================================================"
echo -e "${GREEN}✅ Flujo completo finalizado${NC}"
echo "================================================"
echo ""
echo "📄 Informe guardado en: reports/${DATE}.json"
echo ""

