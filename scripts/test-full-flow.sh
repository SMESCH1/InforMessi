#!/bin/bash
# Script para probar el flujo completo con datos reales del día
# Fase 4 - InforMessi

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 InforMessi - Prueba del Flujo Completo${NC}"
echo "================================================"
echo ""

# Cargar variables de entorno
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo -e "${GREEN}✅ Variables de entorno cargadas${NC}"
else
    echo -e "${RED}❌ Archivo .env no encontrado${NC}"
    exit 1
fi

# Verificar requisitos
echo ""
echo "📋 Verificando requisitos..."

# Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 encontrado${NC}"

# Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Ollama encontrado${NC}"

# Verificar que Ollama esté corriendo
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ollama no está corriendo${NC}"
    echo "   Inicia Ollama: ollama serve"
    exit 1
fi
echo -e "${GREEN}✅ Ollama está corriendo${NC}"

# Verificar modelo
if ! ollama list | grep -q "llama3.2"; then
    echo -e "${YELLOW}⚠️  Modelo llama3.2 no encontrado${NC}"
    echo "   Instalando modelo..."
    ollama pull llama3.2
fi
echo -e "${GREEN}✅ Modelo llama3.2 disponible${NC}"

# Verificar Telegram
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ TELEGRAM_BOT_TOKEN no configurado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Token de Telegram configurado${NC}"

if [ -z "$TELEGRAM_PREVIEW_CHAT_ID" ]; then
    echo -e "${RED}❌ TELEGRAM_PREVIEW_CHAT_ID no configurado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Chat ID de preview configurado${NC}"

echo ""
echo "================================================"
echo "📊 Paso 1: Recolectando datos del día de hoy..."
echo "================================================"
echo ""

# Obtener fecha de hoy
TODAY=$(date +"%Y-%m-%d")
DATA_FILE="/tmp/informessi-data-${TODAY}.json"

echo "📅 Fecha: $TODAY"
echo ""

# Recolectar datos
python3 scripts/collect-daily-data.py --date "$TODAY" --output "$DATA_FILE" 2>&1

if [ ! -s "$DATA_FILE" ]; then
    echo -e "${RED}❌ Error al recolectar datos${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Datos recolectados y guardados en: $DATA_FILE${NC}"
echo ""

# Mostrar resumen de datos
echo "📋 Resumen de datos recolectados:"
python3 -c "
import json
with open('$DATA_FILE', 'r') as f:
    data = json.load(f)
    print(f\"   Fecha: {data['date']}\")
    print(f\"   Días restantes: {data['days_remaining']}\")
    print(f\"   Eventos: {len(data.get('events', []))}\")
    print(f\"   Noticias: {len(data.get('news', []))}\")
    if 'weather' in data:
        print(f\"   Clima AMBA: {data['weather']['amba']['min']}°/{data['weather']['amba']['max']}°\")
        print(f\"   Clima La Plata: {data['weather']['la_plata']['min']}°/{data['weather']['la_plata']['max']}°\")
"

echo ""
echo "================================================"
echo "🤖 Paso 2: Generando mensaje con LLM..."
echo "================================================"
echo ""

MESSAGE_FILE="/tmp/informessi-mensaje-${TODAY}.txt"

python3 scripts/generate-message.py --data "$DATA_FILE" --output "$MESSAGE_FILE" 2>&1 | tail -15

if [ ! -s "$MESSAGE_FILE" ]; then
    echo -e "${RED}❌ Error al generar mensaje${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Mensaje generado y guardado en: $MESSAGE_FILE${NC}"
echo ""

# Mostrar mensaje generado
echo "📄 Mensaje generado:"
echo "----------------------------------------"
head -25 "$MESSAGE_FILE"
echo "----------------------------------------"
echo ""

# Contar palabras
WORD_COUNT=$(wc -w < "$MESSAGE_FILE")
echo "📊 Palabras: $WORD_COUNT"
if [ $WORD_COUNT -ge 90 ] && [ $WORD_COUNT -le 130 ]; then
    echo -e "${GREEN}✅ Longitud apropiada (90-130 palabras)${NC}"
else
    echo -e "${YELLOW}⚠️  Longitud fuera del rango objetivo${NC}"
fi

echo ""
echo "================================================"
echo "📤 Paso 3: Enviando para revisión en Telegram..."
echo "================================================"
echo ""

# Preguntar si quiere esperar respuesta
echo "¿Quieres esperar respuesta de revisión?"
echo "1) Solo enviar preview (sin esperar)"
echo "2) Enviar y esperar respuesta (60 segundos)"
echo "3) Enviar y esperar respuesta (5 minutos)"
echo ""
read -p "Selecciona (1-3): " choice

case $choice in
    1)
        echo ""
        echo "📤 Enviando preview (modo --no-wait)..."
        python3 scripts/telegram-preview.py \
            --message "$(cat $MESSAGE_FILE)" \
            --preview-chat-id "$TELEGRAM_PREVIEW_CHAT_ID" \
            --token "$TELEGRAM_BOT_TOKEN" \
            --no-wait
        echo ""
        echo -e "${GREEN}✅ Preview enviado. Revisa Telegram.${NC}"
        ;;
    2)
        echo ""
        echo "📤 Enviando preview y esperando respuesta (60 segundos)..."
        echo "   Haz click en un botón en Telegram para probar"
        python3 scripts/telegram-preview.py \
            --message "$(cat $MESSAGE_FILE)" \
            --preview-chat-id "$TELEGRAM_PREVIEW_CHAT_ID" \
            --publish-chat-id "${TELEGRAM_PUBLISH_CHAT_ID:-$TELEGRAM_PREVIEW_CHAT_ID}" \
            --token "$TELEGRAM_BOT_TOKEN" \
            --timeout 60
        ;;
    3)
        echo ""
        echo "📤 Enviando preview y esperando respuesta (5 minutos)..."
        echo "   Haz click en un botón en Telegram para probar"
        python3 scripts/telegram-preview.py \
            --message "$(cat $MESSAGE_FILE)" \
            --preview-chat-id "$TELEGRAM_PREVIEW_CHAT_ID" \
            --publish-chat-id "${TELEGRAM_PUBLISH_CHAT_ID:-$TELEGRAM_PREVIEW_CHAT_ID}" \
            --token "$TELEGRAM_BOT_TOKEN" \
            --timeout 300
        ;;
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo "================================================"
echo -e "${GREEN}✅ Flujo completo ejecutado${NC}"
echo "================================================"
echo ""
echo "📁 Archivos generados:"
echo "   - Datos: $DATA_FILE"
echo "   - Mensaje: $MESSAGE_FILE"
echo ""
echo "💡 Tip: Puedes revisar estos archivos para debugging"

