#!/usr/bin/env python3
"""
Script para obtener datos de clima real
Fase 4 - InforMessi
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional

try:
    import requests
except ImportError:
    print("ERROR: Necesitas instalar 'requests': pip install requests")
    sys.exit(1)


def get_weather_openweathermap(api_key: str, city: str, country_code: str = "AR") -> Optional[Dict]:
    """Obtiene clima de OpenWeatherMap"""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{city},{country_code}",
        "appid": api_key,
        "units": "metric",
        "lang": "es"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "min": round(data["main"]["temp_min"]),
            "max": round(data["main"]["temp_max"]),
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Error al obtener clima para {city}: {e}")
        return None


def get_weather_argentina() -> Dict:
    """Obtiene clima para AMBA y La Plata"""
    
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        print("⚠️  WEATHER_API_KEY no configurado, usando datos mock")
        return {
            "amba": {"min": 12, "max": 18, "description": "Parcialmente nublado"},
            "la_plata": {"min": 10, "max": 16, "description": "Parcialmente nublado"},
            "link_argentina": "https://www.smn.gob.ar/pronostico"
        }
    
    # Coordenadas aproximadas
    # AMBA: Buenos Aires
    # La Plata: La Plata, Buenos Aires
    
    amba_weather = get_weather_openweathermap(api_key, "Buenos Aires", "AR")
    la_plata_weather = get_weather_openweathermap(api_key, "La Plata", "AR")
    
    # Si falla, usar valores por defecto
    if not amba_weather:
        amba_weather = {"min": 12, "max": 18, "description": "No disponible"}
    
    if not la_plata_weather:
        la_plata_weather = {"min": 10, "max": 16, "description": "No disponible"}
    
    return {
        "amba": {
            "min": amba_weather["min"],
            "max": amba_weather["max"],
            "description": amba_weather["description"]
        },
        "la_plata": {
            "min": la_plata_weather["min"],
            "max": la_plata_weather["max"],
            "description": la_plata_weather["description"]
        },
        "link_argentina": "https://www.smn.gob.ar/pronostico"
    }


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Obtiene datos de clima real para InforMessi"
    )
    parser.add_argument(
        "--output",
        help="Archivo JSON donde guardar los datos (opcional)"
    )
    parser.add_argument(
        "--api-key",
        help="API key de OpenWeatherMap (o usar WEATHER_API_KEY)"
    )
    
    args = parser.parse_args()
    
    # Cargar API key
    api_key = args.api_key or os.getenv("WEATHER_API_KEY")
    if api_key:
        os.environ["WEATHER_API_KEY"] = api_key
    
    print("🌤 Obteniendo datos de clima...")
    print("=" * 50)
    
    weather = get_weather_argentina()
    
    print(f"📍 AMBA:")
    print(f"   Min: {weather['amba']['min']}°C")
    print(f"   Max: {weather['amba']['max']}°C")
    print(f"   Descripción: {weather['amba']['description']}")
    print()
    print(f"📍 La Plata:")
    print(f"   Min: {weather['la_plata']['min']}°C")
    print(f"   Max: {weather['la_plata']['max']}°C")
    print(f"   Descripción: {weather['la_plata']['description']}")
    print()
    
    # Guardar si se especificó output
    if args.output:
        output_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weather": weather
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Datos guardados en: {args.output}")
    
    # Retornar JSON para uso en scripts (solo JSON, sin texto adicional)
    # Esto permite que otros scripts lo parseen fácilmente
    import sys
    if not args.output:
        # Si no hay output, imprimir solo JSON (para uso en pipes)
        print(json.dumps(weather, ensure_ascii=False))
    else:
        # Si hay output, también imprimir JSON al final para compatibilidad
        print(json.dumps(weather, ensure_ascii=False))


if __name__ == "__main__":
    main()

