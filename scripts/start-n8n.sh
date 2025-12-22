#!/bin/bash
# Script rápido para iniciar n8n con Docker
# InforMessi

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Generar password aleatorio
PASSWORD=$(openssl rand -base64 12 2>/dev/null || date +%s | sha256sum | base64 | head -c 12)

echo -e "${BLUE}🚀 Iniciando n8n con Docker${NC}"
echo "================================"
echo ""

# Verificar si ya existe
if docker ps -a | grep -q n8n; then
    echo -e "${YELLOW}⚠️  n8n ya existe${NC}"
    read -p "¿Reiniciar? (s/N): " restart
    if [[ $restart =~ ^[Ss]$ ]]; then
        docker stop n8n 2>/dev/null || true
        docker rm n8n 2>/dev/null || true
    else
        echo "Iniciando contenedor existente..."
        docker start n8n
        echo ""
        echo -e "${GREEN}✅ n8n iniciado${NC}"
        echo "🌐 Accede a: http://localhost:5678"
        exit 0
    fi
fi

# Crear directorio de datos
mkdir -p ~/n8n-data

# Ejecutar n8n con acceso al host para webhook
docker run -d \
  --name n8n \
  --restart unless-stopped \
  --add-host=host.docker.internal:host-gateway \
  -p 5678:5678 \
  -v ~/n8n-data:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD="$PASSWORD" \
  n8nio/n8n

echo ""
echo -e "${GREEN}✅ n8n iniciado${NC}"
echo ""
echo "🌐 Accede a: http://localhost:5678"
echo "👤 Usuario: admin"
echo -e "${YELLOW}🔑 Contraseña: $PASSWORD${NC}"
echo ""
echo "💡 Comandos útiles:"
echo "   Ver logs: docker logs -f n8n"
echo "   Detener: docker stop n8n"
echo "   Iniciar: docker start n8n"
echo ""

