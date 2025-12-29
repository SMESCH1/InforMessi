#!/bin/bash
# Script para configurar cron automáticamente
# InforMessi - Automatización

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}⏰ Configurando Cron para InforMessi${NC}"
echo "================================================"
echo ""

# Verificar que el script existe
if [ ! -f "$PROJECT_ROOT/scripts/daily-flow.sh" ]; then
    echo "❌ Script daily-flow.sh no encontrado"
    exit 1
fi

# Crear directorio de logs
LOGS_DIR="$HOME/informessi-logs"
mkdir -p "$LOGS_DIR"
echo -e "${GREEN}✅ Directorio de logs: $LOGS_DIR${NC}"

# Crear comando cron
CRON_TIME="${1:-0 8}"  # Default: 8:00 AM
CRON_CMD="cd $PROJECT_ROOT && bash scripts/daily-flow.sh >> $LOGS_DIR/cron-\$(date +\\%Y-\\%m-\\%d).log 2>&1"
CRON_LINE="$CRON_TIME * * * $CRON_CMD"

echo ""
echo "📋 Comando cron a agregar:"
echo "   $CRON_LINE"
echo ""

# Verificar si ya existe
EXISTING=$(crontab -l 2>/dev/null | grep "daily-flow.sh" || true)

if [ -n "$EXISTING" ]; then
    echo -e "${YELLOW}⚠️  Ya existe una entrada de cron para InforMessi:${NC}"
    echo "   $EXISTING"
    echo ""
    read -p "¿Reemplazar? (s/N): " replace
    if [[ $replace =~ ^[Ss]$ ]]; then
        # Remover entrada existente
        crontab -l 2>/dev/null | grep -v "daily-flow.sh" | crontab -
        echo -e "${GREEN}✅ Entrada anterior removida${NC}"
    else
        echo "❌ Cancelado"
        exit 0
    fi
fi

# Agregar nueva entrada
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

echo ""
echo -e "${GREEN}✅ Cron configurado exitosamente${NC}"
echo ""
echo "📋 Crontab actual:"
crontab -l | grep -A 1 -B 1 "daily-flow" || crontab -l
echo ""
echo "💡 Para ver logs:"
echo "   tail -f $LOGS_DIR/cron-\$(date +%Y-%m-%d).log"
echo ""
echo "💡 Para editar:"
echo "   crontab -e"
echo ""

