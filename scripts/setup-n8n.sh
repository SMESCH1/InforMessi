#!/bin/bash
# Script para configurar n8n rápidamente
# InforMessi - Automatización

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Configurando n8n para InforMessi${NC}"
echo "=========================================="
echo ""

# Verificar Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker encontrado${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Docker no encontrado${NC}"
    DOCKER_AVAILABLE=false
fi

# Verificar npm
if command -v npm &> /dev/null; then
    echo -e "${GREEN}✅ npm encontrado${NC}"
    NPM_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  npm no encontrado${NC}"
    NPM_AVAILABLE=false
fi

echo ""

# Crear directorio para datos de n8n
N8N_DATA_DIR="$HOME/n8n-data"
mkdir -p "$N8N_DATA_DIR"
echo -e "${GREEN}✅ Directorio de datos: $N8N_DATA_DIR${NC}"

# Generar password aleatorio
PASSWORD=$(openssl rand -base64 12 2>/dev/null || date +%s | sha256sum | base64 | head -c 12)

echo ""
echo "📋 OPCIONES DE INSTALACIÓN:"
echo "=========================="
echo ""
echo "1️⃣  Docker (Recomendado)"
echo "   - Aislado, fácil de manejar"
echo "   - Requiere Docker instalado"
echo ""
echo "2️⃣  npm (Global)"
echo "   - Instalación directa"
echo "   - Requiere Node.js/npm"
echo ""
echo "3️⃣  npx (Sin instalación)"
echo "   - Ejecuta sin instalar"
echo "   - Requiere Node.js/npm"
echo ""

if [ "$DOCKER_AVAILABLE" = true ]; then
    echo -e "${GREEN}✅ Puedes usar Docker${NC}"
fi

if [ "$NPM_AVAILABLE" = true ]; then
    echo -e "${GREEN}✅ Puedes usar npm/npx${NC}"
fi

echo ""
read -p "¿Qué opción prefieres? (1/2/3): " choice

case $choice in
    1)
        if [ "$DOCKER_AVAILABLE" = false ]; then
            echo -e "${RED}❌ Docker no está instalado${NC}"
            echo "Instala Docker primero: https://docs.docker.com/get-docker/"
            exit 1
        fi
        
        echo ""
        echo "🐳 Configurando n8n con Docker..."
        echo ""
        echo "Comando para ejecutar:"
        echo ""
        echo "docker run -d \\"
        echo "  --name n8n \\"
        echo "  --restart unless-stopped \\"
        echo "  -p 5678:5678 \\"
        echo "  -v $N8N_DATA_DIR:/home/node/.n8n \\"
        echo "  -e N8N_BASIC_AUTH_ACTIVE=true \\"
        echo "  -e N8N_BASIC_AUTH_USER=admin \\"
        echo "  -e N8N_BASIC_AUTH_PASSWORD=$PASSWORD \\"
        echo "  n8nio/n8n"
        echo ""
        echo -e "${YELLOW}⚠️  Guarda esta contraseña: $PASSWORD${NC}"
        echo ""
        read -p "¿Ejecutar ahora? (s/N): " run_now
        
        if [[ $run_now =~ ^[Ss]$ ]]; then
            docker run -d \
              --name n8n \
              --restart unless-stopped \
              -p 5678:5678 \
              -v "$N8N_DATA_DIR:/home/node/.n8n" \
              -e N8N_BASIC_AUTH_ACTIVE=true \
              -e N8N_BASIC_AUTH_USER=admin \
              -e N8N_BASIC_AUTH_PASSWORD="$PASSWORD" \
              n8nio/n8n
            
            echo ""
            echo -e "${GREEN}✅ n8n iniciado con Docker${NC}"
            echo ""
            echo "🌐 Accede a: http://localhost:5678"
            echo "👤 Usuario: admin"
            echo "🔑 Contraseña: $PASSWORD"
            echo ""
            echo "💡 Para ver logs: docker logs -f n8n"
            echo "💡 Para detener: docker stop n8n"
            echo "💡 Para iniciar: docker start n8n"
        else
            echo ""
            echo "📋 Copia y ejecuta el comando manualmente"
        fi
        ;;
    2)
        if [ "$NPM_AVAILABLE" = false ]; then
            echo -e "${RED}❌ npm no está instalado${NC}"
            echo "Instala Node.js primero: https://nodejs.org/"
            exit 1
        fi
        
        echo ""
        echo "📦 Instalando n8n globalmente..."
        npm install n8n -g
        
        echo ""
        echo -e "${GREEN}✅ n8n instalado${NC}"
        echo ""
        echo "🚀 Para iniciar n8n:"
        echo "   n8n start"
        echo ""
        echo "🌐 Luego accede a: http://localhost:5678"
        ;;
    3)
        if [ "$NPM_AVAILABLE" = false ]; then
            echo -e "${RED}❌ npm no está instalado${NC}"
            echo "Instala Node.js primero: https://nodejs.org/"
            exit 1
        fi
        
        echo ""
        echo "🚀 Para ejecutar n8n con npx:"
        echo "   npx n8n"
        echo ""
        echo "🌐 Luego accede a: http://localhost:5678"
        echo ""
        echo -e "${YELLOW}⚠️  Esto ejecutará n8n sin instalarlo permanentemente${NC}"
        ;;
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "=================="
echo ""
echo "1. Accede a n8n en http://localhost:5678"
echo "2. Crea una cuenta o inicia sesión"
echo "3. Ve a 'Workflows' → 'Import from File'"
echo "4. Importa: n8n/workflows/daily-informessi-simple.json"
echo "5. Configura credenciales de Telegram"
echo "6. Ajusta la ruta del script si es necesario"
echo "7. Activa el workflow"
echo ""
echo "📄 Ver guía completa: docs/setup-n8n.md"
echo ""

