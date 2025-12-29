#!/bin/bash
# Script de prueba rápida del sistema de revisión
# Fase 3 - InforMessi

set -e

echo "🚀 InforMessi - Prueba del Sistema de Revisión"
echo "================================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar requisitos
echo "📋 Verificando requisitos..."

# Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 encontrado${NC}"

# requests
if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  requests no instalado. Instalando...${NC}"
    pip install requests
fi
echo -e "${GREEN}✅ requests instalado${NC}"

# Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama no encontrado${NC}"
    echo "   Instala Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
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

# Verificar .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    if [ -f .env.example ]; then
        echo "   Creando .env desde .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}   ⚠️  Edita .env con tus tokens de Telegram${NC}"
    else
        echo -e "${RED}❌ .env.example no encontrado${NC}"
        exit 1
    fi
fi

# Cargar variables de entorno
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✅ Variables de entorno cargadas${NC}"
else
    echo -e "${RED}❌ No se pudo cargar .env${NC}"
    exit 1
fi

# Verificar token de Telegram
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ TELEGRAM_BOT_TOKEN no configurado en .env${NC}"
    echo ""
    echo "Para configurar:"
    echo "1. Habla con @BotFather en Telegram"
    echo "2. Crea un bot con /newbot"
    echo "3. Copia el token a .env"
    exit 1
fi
echo -e "${GREEN}✅ Token de Telegram configurado${NC}"

# Verificar Chat ID
if [ -z "$TELEGRAM_PREVIEW_CHAT_ID" ]; then
    echo -e "${YELLOW}⚠️  TELEGRAM_PREVIEW_CHAT_ID no configurado${NC}"
    echo ""
    echo "Para obtener el Chat ID:"
    echo "1. Crea un grupo privado en Telegram"
    echo "2. Agrega el bot al grupo"
    echo "3. Envía un mensaje al grupo"
    echo "4. Ejecuta: python3 scripts/get-telegram-chat-id.py --token $TELEGRAM_BOT_TOKEN"
    exit 1
fi
echo -e "${GREEN}✅ Chat ID de preview configurado${NC}"

echo ""
echo "================================================"
echo "🧪 Iniciando pruebas..."
echo "================================================"
echo ""

# Generar mensaje
echo "📝 Generando mensaje de prueba..."
TEMP_MSG=$(mktemp)
python3 scripts/generate-message.py --data mock-data.json --output "$TEMP_MSG" 2>&1 | tail -5

if [ ! -s "$TEMP_MSG" ]; then
    echo -e "${RED}❌ Error al generar mensaje${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Mensaje generado${NC}"
echo ""

# Mostrar mensaje generado
echo "📄 Mensaje generado:"
echo "----------------------------------------"
head -20 "$TEMP_MSG"
echo "----------------------------------------"
echo ""

# Preguntar qué prueba hacer
echo "¿Qué prueba quieres hacer?"
echo "1) Solo enviar preview (sin esperar respuesta)"
echo "2) Enviar preview y esperar respuesta (60 segundos)"
echo "3) Enviar preview y esperar respuesta (5 minutos)"
echo ""
read -p "Selecciona (1-3): " choice

case $choice in
    1)
        echo ""
        echo "📤 Enviando preview (modo --no-wait)..."
        python3 scripts/telegram-preview.py \
            --message "$(cat $TEMP_MSG)" \
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
            --message "$(cat $TEMP_MSG)" \
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
            --message "$(cat $TEMP_MSG)" \
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

# Limpiar
rm -f "$TEMP_MSG"

echo ""
echo "================================================"
echo -e "${GREEN}✅ Prueba completada${NC}"
echo "================================================"

