#!/usr/bin/env python3
"""
Script para obtener eventos del día desde data/events.json
Fase 4 - InforMessi
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def get_events_for_date(date: str, events_file: str = "events.json") -> list:
    """Obtiene eventos para una fecha específica"""
    
    filepath = DATA_DIR / events_file
    if not filepath.exists():
        print(f"⚠️  Archivo {events_file} no encontrado")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    events = data.get("events", [])
    
    # Filtrar eventos para la fecha
    today_events = [e for e in events if e.get("date") == date]
    
    # Ordenar por prioridad
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    today_events.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
    
    return today_events


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Obtiene eventos del día para InforMessi"
    )
    parser.add_argument(
        "--date",
        help="Fecha en formato YYYY-MM-DD (default: hoy)",
        default=datetime.now().strftime("%Y-%m-%d")
    )
    parser.add_argument(
        "--events-file",
        default="events.json",
        help="Archivo de eventos (default: events.json)"
    )
    parser.add_argument(
        "--output",
        help="Archivo JSON donde guardar (opcional)"
    )
    
    args = parser.parse_args()
    
    print(f"📅 Obteniendo eventos para {args.date}...")
    print("=" * 50)
    
    events = get_events_for_date(args.date, args.events_file)
    
    if not events:
        print("   No hay eventos para esta fecha")
    else:
        print(f"   Encontrados {len(events)} evento(s):")
        for event in events:
            print(f"   - {event.get('type', 'unknown')}: {event.get('description', 'N/A')}")
    
    # Guardar si se especificó output
    if args.output:
        output_data = {
            "date": args.date,
            "events": events
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Datos guardados en: {args.output}")
    
    # Retornar JSON para uso en scripts
    print(json.dumps(events, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

