#!/bin/bash
# Flujo diario con verificación de PC local y apagado automático de VPS
# Para AWS EC2: Se apaga automáticamente después de ejecutar exitosamente

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Cargar variables de entorno
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Configuración de tiempo límite (en minutos)
MAX_EXECUTION_TIME=${MAX_EXECUTION_TIME:-15}  # 15 minutos por defecto
SHUTDOWN_AFTER_SUCCESS=${SHUTDOWN_AFTER_SUCCESS:-true}  # Apagar después de éxito

# Verificar si PC local está disponible
echo "🔍 Verificando disponibilidad de PC local..."
python3 scripts/check-pc-available.py

if [ $? -eq 0 ]; then
    echo "✅ PC local está disponible"
    echo "   No ejecutando en VPS (PC local lo hará)"
    echo ""
    echo "💤 Apagando VPS para ahorrar horas de free tier..."
    bash scripts/shutdown-instance.sh
    exit 0
fi

echo "⚠️  PC local NO está disponible"
echo "   Ejecutando en VPS (fallback)..."
echo ""

# Configurar timeout para la ejecución
TIMEOUT_CMD="timeout ${MAX_EXECUTION_TIME}m"

# Ejecutar flujo normal con timeout
echo "⏱️  Tiempo límite de ejecución: ${MAX_EXECUTION_TIME} minutos"
echo ""

if $TIMEOUT_CMD bash scripts/daily-flow.sh; then
    EXIT_CODE=$?
    echo ""
    echo "================================================"
    echo "✅ Flujo ejecutado exitosamente"
    echo "================================================"
    
    if [ "$SHUTDOWN_AFTER_SUCCESS" = "true" ]; then
        echo ""
        echo "💤 Apagando VPS para ahorrar horas de free tier..."
        bash scripts/shutdown-instance.sh
    fi
    
    exit $EXIT_CODE
else
    EXIT_CODE=$?
    echo ""
    echo "================================================"
    echo "❌ Flujo falló o excedió tiempo límite"
    echo "================================================"
    
    # No apagar si falló, para poder investigar
    echo "⚠️  VPS permanecerá encendida para investigar el error"
    echo "   Revisa los logs: ~/informessi-logs/"
    
    exit $EXIT_CODE
fi

