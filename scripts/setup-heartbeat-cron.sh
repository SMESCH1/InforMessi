#!/bin/bash
# Configura cron para enviar heartbeat diariamente a las 8:00 AM

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/heartbeat.py"

echo "🔧 Configurando cron para heartbeat de InforMessi"
echo ""

# Crear directorio de logs si no existe
mkdir -p ~/informessi-logs

# Crear entrada de cron
CRON_ENTRY="0 8 * * * cd ${PROJECT_ROOT} && python3 ${SCRIPT_PATH} >> ~/informessi-logs/heartbeat-\$(date +\\%Y-\\%m-\\%d).log 2>&1"

# Verificar si ya existe
if crontab -l 2>/dev/null | grep -q "heartbeat.py"; then
    echo "⚠️  Ya existe una entrada de cron para heartbeat"
    echo ""
    echo "Entrada actual:"
    crontab -l | grep "heartbeat.py"
    echo ""
    echo "¿Reemplazar con la nueva configuración? (s/n)"
    read -r response
    if [[ ! "$response" =~ ^[Ss]$ ]]; then
        echo "❌ Cancelado"
        exit 0
    fi
    
    # Eliminar entrada antigua
    crontab -l 2>/dev/null | grep -v "heartbeat.py" | crontab -
fi

# Agregar nueva entrada
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✅ Cron configurado exitosamente"
echo ""
echo "📋 Entrada agregada:"
crontab -l | grep "heartbeat.py"
echo ""
echo "💡 El heartbeat se enviará todos los días a las 8:00 AM"
echo "   Logs: ~/informessi-logs/heartbeat-YYYY-MM-DD.log"
echo ""
echo "🧪 ¿Probar ahora? (s/n)"
read -r response
if [[ "$response" =~ ^[Ss]$ ]]; then
    echo ""
    echo "Enviando heartbeat de prueba..."
    python3 "$SCRIPT_PATH"
fi

