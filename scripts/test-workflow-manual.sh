#!/bin/bash
# Script para simular el workflow de GitHub Actions manualmente
# Útil para probar el flujo completo antes de que se ejecute automáticamente

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Fecha objetivo (por defecto mañana, o se puede pasar como argumento)
if [ -z "$1" ]; then
    TARGET_DATE=$(date -d "+1 day" +%Y-%m-%d 2>/dev/null || date -v+1d +%Y-%m-%d 2>/dev/null || python3 -c "from datetime import datetime, timedelta; print((datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))")
else
    TARGET_DATE="$1"
fi

echo -e "${BLUE}🧪 Simulación del Workflow de GitHub Actions${NC}"
echo "================================================"
echo -e "${YELLOW}📅 Fecha objetivo: ${TARGET_DATE}${NC}"
echo "================================================"
echo ""

# Activar venv si existe
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Entorno virtual activado${NC}"
else
    echo -e "${YELLOW}⚠️  Entorno virtual no encontrado${NC}"
fi

# Cargar variables de entorno
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo -e "${GREEN}✅ Variables de entorno cargadas${NC}"
else
    echo -e "${RED}❌ Archivo .env no encontrado${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}Paso 1: Verificar si existe el informe${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

if [ ! -f "reports/${TARGET_DATE}.json" ]; then
    echo -e "${YELLOW}📝 Informe para ${TARGET_DATE} no existe, generando...${NC}"
    python3 scripts/generate-advance-reports.py --days 1 --start-date ${TARGET_DATE} || {
        echo -e "${RED}⚠️  Error al generar, continuando...${NC}"
    }
else
    echo -e "${GREEN}✅ Informe para ${TARGET_DATE} ya existe${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}Paso 2: Actualizar informe del día${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Actualizar informe con datos recientes
python3 scripts/update-today-report.py --date ${TARGET_DATE} || {
    echo -e "${YELLOW}⚠️  Error al actualizar, continuando...${NC}"
}

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}Paso 3: Diagnóstico de configuración${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Diagnóstico (sin enviar mensajes de prueba)
python3 scripts/diagnose-workflow.py || {
    echo -e "${YELLOW}⚠️  Error en diagnóstico${NC}"
}

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}Paso 4: Enviar a revisión o publicar${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Verificar si está pre-aprobado antes de enviar
python3 << PYEOF
import json
from pathlib import Path

report_file = Path(f"reports/${TARGET_DATE}.json")
if report_file.exists():
    r = json.load(open(report_file))
    if r.get("pre_approved"):
        print("✅ Informe está PRE-APROBADO - se publicará directamente")
    else:
        print("📨 Informe NO está pre-aprobado - se enviará a preview")
PYEOF

# Enviar a Telegram (si está pre-aprobado, se publica directamente)
python3 scripts/send-daily-report-review.py --date ${TARGET_DATE} || {
    echo -e "${YELLOW}⚠️  Error al enviar, continuando...${NC}"
}

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}Paso 5: Publicación automática de respaldo${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Verificar informes que no fueron publicados (con horas muy bajas para testing)
echo -e "${YELLOW}💡 Verificando publicación automática (con 0.1 horas para testing)...${NC}"
python3 scripts/auto-publish-fallback.py --check-all --hours 0.1 || {
    echo -e "${YELLOW}⚠️  Error en publicación automática, continuando...${NC}"
}

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Simulación del workflow completada${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📋 Verificación final:${NC}"
python3 << PYEOF
import json
from pathlib import Path

target_date = "${TARGET_DATE}"
report_file = Path(f"reports/{target_date}.json")
if report_file.exists():
    r = json.load(open(report_file))
    print(f"   Fecha: {target_date}")
    print(f"   Pre-aprobado: {r.get('pre_approved', False)}")
    print(f"   Estado: {r.get('status', 'N/A')}")
    print(f"   Publicado: {'Sí' if r.get('published_at') else 'No'}")
    if r.get('published_at'):
        print(f"   Fecha publicación: {r.get('published_at')}")
else:
    print(f"   ❌ Informe no existe")
PYEOF

echo ""
echo -e "${GREEN}💡 Revisa los mensajes en Telegram para verificar${NC}"

