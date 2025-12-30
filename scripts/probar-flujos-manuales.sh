#!/bin/bash
# Script para probar flujos manualmente
# MVP - InforMessi

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${BLUE}🧪 Pruebas Manuales de Flujos - InforMessi${NC}"
echo "================================================"
echo ""

# Fecha de prueba (mañana)
TEST_DATE=$(date -d "+1 day" +"%Y-%m-%d" 2>/dev/null || date -v+1d +"%Y-%m-%d" 2>/dev/null || python3 -c "from datetime import datetime, timedelta; print((datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))")

echo -e "${YELLOW}📅 Fecha de prueba: ${TEST_DATE}${NC}"
echo ""

# Prueba 1: Generación
echo -e "${BLUE}1️⃣  PRUEBA: Generación de Informe${NC}"
echo "   Generando informe para ${TEST_DATE}..."
python3 scripts/generate-advance-reports.py --days 1 --start-date ${TEST_DATE}
echo -e "   ${GREEN}✅ Informe generado${NC}"
echo ""

# Prueba 2: Edición y Pre-Aprobación
echo -e "${BLUE}2️⃣  PRUEBA: Edición y Pre-Aprobación${NC}"
echo "   Ejecutando script de edición..."
echo "   ${YELLOW}💡 Selecciona opción 2: 'Validar sin editar'${NC}"
python3 scripts/edit-and-validate-report.py --date ${TEST_DATE} || echo "   ⚠️  Edición cancelada o falló"
echo ""

# Prueba 3: Verificar Pre-Aprobación
echo -e "${BLUE}3️⃣  PRUEBA: Verificar Pre-Aprobación${NC}"
REPORT_FILE="reports/${TEST_DATE}.json"
if [ -f "$REPORT_FILE" ]; then
    PRE_APPROVED=$(python3 -c "import json; r=json.load(open('$REPORT_FILE')); print(r.get('pre_approved', False))")
    if [ "$PRE_APPROVED" = "True" ]; then
        echo -e "   ${GREEN}✅ Informe está pre-aprobado${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Informe NO está pre-aprobado${NC}"
        echo "   Ejecuta: python3 scripts/edit-and-validate-report.py --date ${TEST_DATE}"
    fi
else
    echo -e "   ${YELLOW}⚠️  Informe no encontrado${NC}"
fi
echo ""

# Prueba 4: Envío (debería publicar directamente si está pre-aprobado)
echo -e "${BLUE}4️⃣  PRUEBA: Envío (debería publicar directamente si está pre-aprobado)${NC}"
echo "   Enviando informe..."
python3 scripts/send-daily-report-review.py --date ${TEST_DATE} || echo "   ⚠️  Error al enviar"
echo ""

echo "================================================"
echo -e "${GREEN}✅ Pruebas completadas${NC}"
echo "================================================"
echo ""
echo "📋 Verificaciones:"
echo "   1. ¿Se generó el informe? → reports/${TEST_DATE}.json"
echo "   2. ¿Está pre-aprobado? → Verifica en el JSON"
echo "   3. ¿Se publicó directamente? → Revisa el grupo público de Telegram"
echo ""

