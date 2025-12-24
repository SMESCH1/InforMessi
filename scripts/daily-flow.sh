#!/bin/bash
# Flujo diario completo de InforMessi
# Ejecuta: recolección → generación → revisión

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
DATA_FILE="/tmp/informessi-datos-${DATE}.json"
MESSAGE_FILE="/tmp/informessi-mensaje-${DATE}.txt"

echo -e "${BLUE}🚀 InforMessi - Flujo Diario Completo${NC}"
echo "================================================"
echo ""

# Paso 1: Recolectar datos
echo -e "${BLUE}📊 Paso 1: Recolectando datos del día...${NC}"
python3 scripts/collect-daily-data.py \
  --date "$DATE" \
  --output "$DATA_FILE" 2>&1 | tail -8

if [ ! -f "$DATA_FILE" ]; then
    echo "❌ Error al recolectar datos"
    exit 1
fi

echo ""
echo -e "${BLUE}📝 Paso 2: Generando mensaje...${NC}"
python3 scripts/generate-message.py \
  --data "$DATA_FILE" \
  --output "$MESSAGE_FILE" 2>&1 | tail -15

if [ ! -f "$MESSAGE_FILE" ]; then
    echo "❌ Error al generar mensaje"
    exit 1
fi

echo ""
echo -e "${BLUE}📤 Paso 3: Enviando para revisión en Telegram...${NC}"

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_PREVIEW_CHAT_ID" ]; then
    echo -e "${YELLOW}⚠️  Variables de Telegram no configuradas${NC}"
    echo "   Mensaje generado en: $MESSAGE_FILE"
    echo "   Configura TELEGRAM_BOT_TOKEN y TELEGRAM_PREVIEW_CHAT_ID en .env"
    exit 0
fi

# Ajustar OLLAMA_BASE_URL si estamos en Docker
if [ -n "$OLLAMA_BASE_URL" ]; then
    export OLLAMA_BASE_URL
else
    export OLLAMA_BASE_URL="http://ollama:11434"
fi

python3 scripts/telegram-preview.py \
  --message "$(cat $MESSAGE_FILE)" \
  --preview-chat-id "$TELEGRAM_PREVIEW_CHAT_ID" \
  --token "$TELEGRAM_BOT_TOKEN" \
  --no-wait 2>&1 | tail -10

echo ""
echo "================================================"
echo -e "${GREEN}✅ Flujo completo finalizado${NC}"
echo "================================================"
echo ""
echo "📄 Archivos generados:"
echo "   Datos: $DATA_FILE"
echo "   Mensaje: $MESSAGE_FILE"
echo ""

