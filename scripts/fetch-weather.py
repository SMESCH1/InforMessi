#!/usr/bin/env python3
"""
Obtiene el clima (min/max) para AMBA y La Plata usando Open-Meteo (sin API key).

Fase 1 - InforMessi
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from time_utils import now_ar_iso, today_ar

import requests

# Evita UnicodeEncodeError en consolas Windows (cp1252) al imprimir emojis
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 15

LOCATIONS = {
    "amba": {"latitude": -34.61, "longitude": -58.38},
    "la_plata": {"latitude": -34.92, "longitude": -57.95},
}

SMN_LINK = "https://www.smn.gob.ar/pronostico"


def _fetch_location(key: str, date: str) -> dict | None:
    """Pide el forecast diario para una ubicación. Retorna {"min": int, "max": int} o None."""
    coords = LOCATIONS[key]
    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "daily": "temperature_2m_min,temperature_2m_max",
        "timezone": "America/Argentina/Buenos_Aires",
        "start_date": date,
        "end_date": date,
    }

    response = requests.get(OPEN_METEO_URL, params=params, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()

    daily = payload.get("daily") or {}
    mins = daily.get("temperature_2m_min") or []
    maxs = daily.get("temperature_2m_max") or []

    if not mins or not maxs:
        return None
    if mins[0] is None or maxs[0] is None:
        return None

    return {"min": round(mins[0]), "max": round(maxs[0])}


def get_weather(date: str) -> dict | None:
    """
    Obtiene el clima (min/max) para AMBA y La Plata en la fecha dada.

    Retorna None si hay error de red/HTTP, la respuesta no trae datos, o la
    fecha está fuera del horizonte de forecast de Open-Meteo. Nunca lanza
    excepción hacia afuera.
    """
    try:
        amba = _fetch_location("amba", date)
        la_plata = _fetch_location("la_plata", date)
    except Exception as e:
        print(f"⚠️  Error al obtener clima: {e}")
        return None

    if amba is None or la_plata is None:
        print("⚠️  Clima no disponible para la fecha solicitada (fuera de horizonte de forecast).")
        return None

    return {
        "amba": amba,
        "la_plata": la_plata,
        "fetched_at": now_ar_iso(),
        "source": "open-meteo",
    }


def format_weather_block(weather: dict) -> str:
    """Formatea el bloque de clima según docs/editorial-guide.md."""
    amba = weather["amba"]
    la_plata = weather["la_plata"]

    return (
        "🌤 Clima\n"
        f"AMBA: min {amba['min']}° / max {amba['max']}°\n"
        f"La Plata: min {la_plata['min']}° / max {la_plata['max']}°\n"
        f"Clima en otras partes de Argentina: {SMN_LINK}"
    )


def main():
    """Función principal"""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Obtiene el clima de AMBA y La Plata para una fecha"
    )
    parser.add_argument(
        "--date",
        help="Fecha en formato YYYY-MM-DD (default: hoy)",
        default=today_ar(),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprimir el resultado como JSON",
    )

    args = parser.parse_args()

    weather = get_weather(args.date)

    if args.json:
        print(json.dumps(weather, ensure_ascii=False) if weather else "null")
    else:
        if weather:
            print(format_weather_block(weather))
        else:
            print("⚠️  No se pudo obtener el clima.")


if __name__ == "__main__":
    main()
