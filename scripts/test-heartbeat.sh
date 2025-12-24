#!/bin/bash
# Script de prueba para verificar heartbeat

set -e

echo "🧪 Prueba de Heartbeat - InforMessi"
echo "===================================="
echo ""

# Cargar variables de entorno
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

VPS_HEARTBEAT_URL=${VPS_HEARTBEAT_URL:-"http://localhost:8080"}
PC_ID=${PC_ID:-"pc-sebastian"}

echo "📋 Configuración:"
echo "   VPS URL: $VPS_HEARTBEAT_URL"
echo "   PC ID: $PC_ID"
echo ""

# Verificar estado del servidor
echo "1️⃣ Verificando estado del servidor..."
STATUS=$(curl -s "$VPS_HEARTBEAT_URL/status" || echo "ERROR")
if [ "$STATUS" = "ERROR" ]; then
    echo "❌ No se puede conectar al servidor de heartbeat"
    echo "   Verifica que el servidor esté corriendo y la URL sea correcta"
    exit 1
fi
echo "✅ Servidor respondiendo: $STATUS"
echo ""

# Verificar disponibilidad de PC
echo "2️⃣ Verificando disponibilidad de PC local..."
CHECK=$(curl -s "$VPS_HEARTBEAT_URL/check/$PC_ID")
echo "$CHECK" | python3 -m json.tool
echo ""

# Enviar heartbeat de prueba
echo "3️⃣ Enviando heartbeat de prueba..."
RESPONSE=$(curl -s -X POST "$VPS_HEARTBEAT_URL/heartbeat" \
    -H "Content-Type: application/json" \
    -d "{\"pc_id\":\"$PC_ID\",\"timestamp\":\"$(date -Iseconds)\",\"status\":\"online\",\"work_time\":true}")
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Verificar nuevamente
echo "4️⃣ Verificando disponibilidad después del heartbeat..."
sleep 2
CHECK=$(curl -s "$VPS_HEARTBEAT_URL/check/$PC_ID")
echo "$CHECK" | python3 -m json.tool
echo ""

echo "✅ Prueba completada"

