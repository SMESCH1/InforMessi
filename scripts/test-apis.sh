#!/bin/bash
# Script para probar todas las APIs configuradas
# InforMessi - Fase 4

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Prueba de APIs - InforMessi${NC}"
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

echo ""
echo "================================================"
echo "1️⃣  Probando Clima..."
echo "================================================"
echo ""

if [ -z "$WEATHER_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  WEATHER_API_KEY no configurado${NC}"
    echo "   El sistema usará datos por defecto"
else
    echo -e "${GREEN}✅ WEATHER_API_KEY configurado${NC}"
fi

python3 scripts/fetch-weather.py 2>&1 | tail -10

echo ""
echo "================================================"
echo "2️⃣  Probando Noticias..."
echo "================================================"
echo ""

if [ -z "$NEWSAPI_KEY" ]; then
    echo -e "${YELLOW}⚠️  NEWSAPI_KEY no configurado (opcional)${NC}"
    echo "   Se usarán RSS feeds y scraping"
else
    echo -e "${GREEN}✅ NEWSAPI_KEY configurado${NC}"
fi

python3 scripts/fetch-news.py --max-results 3 2>&1 | tail -15

echo ""
echo "================================================"
echo "3️⃣  Probando Eventos..."
echo "================================================"
echo ""

TODAY=$(date +"%Y-%m-%d")
python3 scripts/fetch-events-enhanced.py --date "$TODAY" 2>&1 | tail -15

echo ""
echo "================================================"
echo "4️⃣  Probando Recolección Completa..."
echo "================================================"
echo ""

python3 scripts/collect-daily-data.py --date "$TODAY" --output /tmp/test-apis.json 2>&1 | tail -20

echo ""
echo "================================================"
echo "📊 Resumen de Datos Recolectados:"
echo "================================================"
echo ""

if [ -f /tmp/test-apis.json ]; then
    python3 -c "
import json
with open('/tmp/test-apis.json', 'r') as f:
    data = json.load(f)
    print(f\"Fecha: {data['date']}\")
    print(f\"Días restantes: {data['days_remaining']}\")
    print(f\"Eventos: {len(data.get('events', []))}\")
    print(f\"Noticias: {len(data.get('news', []))}\")
    if 'weather' in data:
        print(f\"Clima AMBA: {data['weather']['amba']['min']}°/{data['weather']['amba']['max']}°\")
"
    echo ""
    echo -e "${GREEN}✅ Datos guardados en: /tmp/test-apis.json${NC}"
else
    echo -e "${RED}❌ Error al recolectar datos${NC}"
fi

echo ""
echo "================================================"
echo -e "${GREEN}✅ Prueba completada${NC}"
echo "================================================"

