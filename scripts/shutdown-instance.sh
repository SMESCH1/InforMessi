#!/bin/bash
# Script para apagar la instancia EC2 automáticamente
# Ahorra horas de free tier cuando no se necesita la VPS

set -e

# Cargar variables de entorno
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Verificar si AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo "⚠️  AWS CLI no está instalado"
    echo "   La instancia no se apagará automáticamente"
    echo "   Para instalarlo: sudo apt install awscli"
    exit 0
fi

# Obtener ID de instancia desde metadata
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo "")

if [ -z "$INSTANCE_ID" ]; then
    echo "⚠️  No se pudo obtener el ID de instancia"
    echo "   Esto puede no ser una instancia EC2"
    exit 0
fi

# Verificar región
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region 2>/dev/null || echo "us-east-1")

echo "🛑 Apagando instancia EC2..."
echo "   Instance ID: $INSTANCE_ID"
echo "   Region: $REGION"
echo ""

# Detener instancia
if aws ec2 stop-instances --instance-ids "$INSTANCE_ID" --region "$REGION" > /dev/null 2>&1; then
    echo "✅ Instancia detenida exitosamente"
    echo "   La instancia se apagará en unos momentos"
    echo "   Para encenderla de nuevo, usa AWS Console o:"
    echo "   aws ec2 start-instances --instance-ids $INSTANCE_ID --region $REGION"
else
    echo "⚠️  No se pudo detener la instancia automáticamente"
    echo "   Puede que no tengas permisos o no estés en EC2"
    echo "   Detén la instancia manualmente desde AWS Console"
fi

