#!/bin/bash
# Configura heartbeat como servicio systemd en PC local

set -e

SERVICE_NAME="informessi-heartbeat"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/heartbeat.py"

echo "🔧 Configurando servicio de heartbeat para InforMessi"
echo ""

# Verificar que el script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Error: No se encuentra heartbeat.py en $SCRIPT_PATH"
    exit 1
fi

# Crear directorio de systemd user si no existe
mkdir -p ~/.config/systemd/user

# Crear archivo de servicio
cat > ~/.config/systemd/user/${SERVICE_NAME}.service <<EOF
[Unit]
Description=InforMessi Heartbeat
After=network.target

[Service]
Type=simple
WorkingDirectory=${PROJECT_ROOT}
ExecStart=/usr/bin/python3 ${SCRIPT_PATH}
Restart=always
RestartSec=60
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=${PROJECT_ROOT}/.env

[Install]
WantedBy=default.target
EOF

echo "✅ Archivo de servicio creado: ~/.config/systemd/user/${SERVICE_NAME}.service"
echo ""

# Recargar systemd
systemctl --user daemon-reload

# Habilitar servicio
systemctl --user enable ${SERVICE_NAME}

echo "✅ Servicio habilitado"
echo ""
echo "📋 Comandos útiles:"
echo "   Iniciar: systemctl --user start ${SERVICE_NAME}"
echo "   Detener: systemctl --user stop ${SERVICE_NAME}"
echo "   Estado: systemctl --user status ${SERVICE_NAME}"
echo "   Logs: journalctl --user -u ${SERVICE_NAME} -f"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   El heartbeat ahora se envía UNA VEZ al día, temprano en la mañana"
echo "   Configura un cron para ejecutarlo antes de las 10:15 AM"
echo ""
echo "   Ejemplo de cron (ejecuta a las 8:00 AM):"
echo "   0 8 * * * cd ${PROJECT_ROOT} && python3 ${SCRIPT_PATH}"
echo ""
echo "🚀 ¿Iniciar el servicio ahora? (s/n)"
read -r response
if [[ "$response" =~ ^[Ss]$ ]]; then
    systemctl --user start ${SERVICE_NAME}
    echo "✅ Servicio iniciado"
    systemctl --user status ${SERVICE_NAME}
fi

