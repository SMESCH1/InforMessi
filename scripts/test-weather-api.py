#!/usr/bin/env python3
"""
Script para probar la API de clima y diagnosticar problemas
"""

import os
import sys
import requests

# Cargar variables de entorno
from pathlib import Path
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

api_key = os.getenv("WEATHER_API_KEY")

print("🔍 Diagnóstico de API de Clima")
print("=" * 50)
print()

if not api_key:
    print("❌ WEATHER_API_KEY no encontrado en .env")
    sys.exit(1)

if api_key == "your_weather_api_key":
    print("❌ WEATHER_API_KEY es un placeholder, necesitas una key real")
    sys.exit(1)

print(f"✅ API Key encontrada: {api_key[:10]}...{api_key[-4:]}")
print(f"   Longitud: {len(api_key)} caracteres")
print()

# Probar con Buenos Aires
print("🌤 Probando con Buenos Aires...")
url = "http://api.openweathermap.org/data/2.5/weather"
params = {
    "q": "Buenos Aires,AR",
    "appid": api_key,
    "units": "metric",
    "lang": "es"
}

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ API funcionando correctamente")
        print(f"   Temperatura: {data['main']['temp']}°C")
        print(f"   Min: {data['main']['temp_min']}°C")
        print(f"   Max: {data['main']['temp_max']}°C")
        print(f"   Descripción: {data['weather'][0]['description']}")
    elif response.status_code == 401:
        print("   ❌ Error 401: API key inválida o no activada")
        print("   💡 Solución:")
        print("      1. Verifica que copiaste la key completa")
        print("      2. Espera 10 minutos después de crear la cuenta (activación)")
        print("      3. Verifica en https://home.openweathermap.org/api_keys")
    elif response.status_code == 429:
        print("   ❌ Error 429: Límite de requests excedido")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Respuesta: {response.text[:200]}")
        
except requests.exceptions.RequestException as e:
    print(f"   ❌ Error de conexión: {e}")

print()
print("=" * 50)

