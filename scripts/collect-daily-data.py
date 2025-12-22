#!/usr/bin/env python3
"""
Script para recolectar todos los datos del día (clima, eventos, noticias)
Fase 4 - InforMessi
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def collect_all_data(date: str = None) -> dict:
    """Recolecta todos los datos del día"""
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    print("📊 Recolectando datos del día...")
    print("=" * 50)
    
    # Clima: Removido (feature futura)
    # El clima se dejó como feature futura, no se incluye en el flujo actual
    
    # Eventos - usar script mejorado
    print("📅 Obteniendo eventos...")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "fetch-events-enhanced.py"), "--date", date],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # Buscar JSON en la salida
            output_lines = result.stdout.strip().split('\n')
            json_line = None
            for line in reversed(output_lines):
                line = line.strip()
                if line.startswith('[') or line.startswith('{'):
                    try:
                        events = json.loads(line)
                        break
                    except:
                        continue
            else:
                events = []
        else:
            events = []
    except Exception as e:
        print(f"⚠️  Error al obtener eventos: {e}, usando solo JSON")
        # Fallback a JSON directo
        events_file = PROJECT_ROOT / "data" / "events.json"
        events = []
        if events_file.exists():
            with open(events_file, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
                events = [e for e in events_data.get("events", []) if e.get("date") == date]
    
    # Noticias - usar script de noticias
    print("📰 Obteniendo noticias...")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "fetch-news.py"), "--max-results", "3", "--json-only"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # Buscar JSON en la salida (puede haber mensajes antes)
            output = result.stdout.strip()
            # Buscar la línea que empieza con [
            json_found = False
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('['):
                    try:
                        news = json.loads(line)
                        json_found = True
                        break
                    except json.JSONDecodeError:
                        # Puede ser JSON multilínea, intentar concatenar
                        continue
            if not json_found:
                # Intentar parsear toda la salida como JSON
                try:
                    news = json.loads(output)
                except:
                    news = []
        else:
            news = []
    except Exception as e:
        print(f"⚠️  Error al obtener noticias: {e}")
        news = []
    
    # Calcular días restantes
    mundial_start = "2026-06-11"
    mundial = datetime.strptime(mundial_start, "%Y-%m-%d").date()
    current = datetime.strptime(date, "%Y-%m-%d").date()
    days_remaining = (mundial - current).days
    
    data = {
        "date": date,
        "mundial_2026_start": mundial_start,
        "days_remaining": days_remaining,
        "events": events,
        "news": news
    }
    
    print()
    print("✅ Datos recolectados:")
    print(f"   Fecha: {date}")
    print(f"   Días restantes: {days_remaining}")
    print(f"   Eventos: {len(events)}")
    print(f"   Noticias: {len(news)}")
    
    return data


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Recolecta todos los datos del día para InforMessi"
    )
    parser.add_argument(
        "--date",
        help="Fecha en formato YYYY-MM-DD (default: hoy)",
        default=datetime.now().strftime("%Y-%m-%d")
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Archivo JSON donde guardar los datos"
    )
    
    args = parser.parse_args()
    
    data = collect_all_data(args.date)
    
    # Guardar
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Datos guardados en: {args.output}")


if __name__ == "__main__":
    main()

