#!/bin/bash
# Script para configurar el entorno virtual de InforMessi

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Configurando entorno virtual para InforMessi${NC}"
echo "================================================"
echo ""

# Verificar si venv existe
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  El entorno virtual ya existe${NC}"
    read -p "¿Recrear? (s/N): " recreate
    if [[ $recreate =~ ^[Ss]$ ]]; then
        echo "Eliminando venv existente..."
        rm -rf venv
    else
        echo "Usando venv existente"
    fi
fi

# Crear venv si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
fi

# Activar venv
echo ""
echo "🔌 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip --quiet

# Instalar dependencias
echo "📥 Instalando dependencias..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install requests beautifulsoup4 feedparser
fi

echo ""
echo "================================================"
echo -e "${GREEN}✅ Entorno virtual configurado${NC}"
echo "================================================"
echo ""
echo "💡 Para activar el venv en el futuro, ejecuta:"
echo "   source venv/bin/activate"
echo ""
echo "💡 Para desactivar:"
echo "   deactivate"
echo ""

