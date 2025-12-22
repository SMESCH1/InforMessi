#!/bin/bash
# Script de diagnóstico completo para API de clima

source venv/bin/activate
export $(grep -v '^#' .env | grep -v '^$' | xargs)

echo "🔍 Diagnóstico Completo de API de Clima"
echo "================================================"
echo ""

# Verificar API key
if [ -z "$WEATHER_API_KEY" ]; then
    echo "❌ WEATHER_API_KEY no configurada"
    exit 1
fi

echo "✅ API Key encontrada: ${WEATHER_API_KEY:0:10}...${WEATHER_API_KEY: -4}"
echo "   Longitud: ${#WEATHER_API_KEY} caracteres"
echo ""

# Probar diferentes endpoints
echo "🌤 Probando diferentes endpoints..."
echo ""

# Endpoint 1: Current Weather
echo "1. Current Weather API:"
response=$(curl -s -w "\n%{http_code}" "http://api.openweathermap.org/data/2.5/weather?q=Buenos Aires,AR&appid=$WEATHER_API_KEY&units=metric&lang=es")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)

echo "   Status: $http_code"
if [ "$http_code" = "200" ]; then
    echo "   ✅ Funcionando correctamente"
    echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Temp: {d['main']['temp']}°C, {d['weather'][0]['description']}\")" 2>/dev/null
elif [ "$http_code" = "401" ]; then
    echo "   ❌ Error 401: API key inválida"
    echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Mensaje: {d.get('message', 'N/A')}\")" 2>/dev/null || echo "   Respuesta: $body"
elif [ "$http_code" = "429" ]; then
    echo "   ⚠️  Error 429: Límite de requests excedido"
else
    echo "   ❌ Error $http_code"
    echo "   Respuesta: $body"
fi

echo ""

# Verificar si la key tiene espacios
if [[ "$WEATHER_API_KEY" =~ [[:space:]] ]]; then
    echo "⚠️  ADVERTENCIA: La API key contiene espacios"
    echo "   Esto puede causar problemas. Verifica tu .env"
fi

echo ""
echo "================================================"
echo "💡 Soluciones posibles:"
echo ""
echo "1. Verifica en https://home.openweathermap.org/api_keys:"
echo "   - ¿La key aparece en la lista?"
echo "   - ¿Está activa (no revocada)?"
echo ""
echo "2. Si acabas de crear la cuenta:"
echo "   - Espera hasta 2 horas (a veces toma más tiempo)"
echo "   - Verifica que confirmaste el email"
echo ""
echo "3. Si la key es antigua:"
echo "   - Genera una nueva key"
echo "   - Actualiza .env con la nueva key"
echo ""
echo "4. Verifica el formato en .env:"
echo "   - No debe tener espacios: WEATHER_API_KEY=abc123..."
echo "   - No debe tener comillas"
echo ""

