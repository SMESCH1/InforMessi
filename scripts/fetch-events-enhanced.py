#!/usr/bin/env python3
"""
Script mejorado para obtener eventos del día
Incluye: archivo JSON, Wikipedia, y scraping de webs deportivas
Fase 4 - InforMessi
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Necesitas instalar 'requests' y 'beautifulsoup4':")
    print("  pip install requests beautifulsoup4")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def get_events_from_json(date: str, events_file: str = "events.json") -> List[Dict]:
    """Obtiene eventos desde archivo JSON, matcheando por MM-DD"""
    filepath = DATA_DIR / events_file
    if not filepath.exists():
        return []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        events = data.get("events", [])
        date_key = date[5:]  # MM-DD
        target_year = int(date[:4])
        today_events = []
        for event in events:
            event_date = event.get("date", "")
            if len(event_date) < 10 or event_date[5:] != date_key:
                continue

            ev = dict(event)

            if ev.get("type") == "birthday" and "age" in ev:
                event_year = int(event_date[:4])
                birth_year = event_year - ev["age"]
                ev["age"] = target_year - birth_year
                ev["description"] = (
                    f"Cumpleaños de {ev.get('person', '')} ({ev['age']} años)"
                )

            today_events.append(ev)

        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        today_events.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))

        return today_events
    except Exception as e:
        print(f"⚠️  Error al leer eventos.json: {e}")
        return []


def get_events_wikipedia(date: str) -> List[Dict]:
    """Obtiene eventos históricos de fútbol desde Wikipedia"""
    try:
        # Formato: DD de mes (ej: "22 de diciembre")
        day = datetime.strptime(date, "%Y-%m-%d").day
        month_names = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        month = datetime.strptime(date, "%Y-%m-%d").month
        date_str = f"{day} de {month_names[month]}"
        
        # Buscar en Wikipedia (API)
        url = "https://es.wikipedia.org/api/rest_v1/page/summary"
        
        # Páginas relevantes para eventos de fútbol
        pages = [
            f"Anexo:Hechos_relevantes_de_{month_names[month]}_en_el_fútbol",
            f"{date_str}_en_el_fútbol",
        ]
        
        events = []
        for page in pages:
            try:
                response = requests.get(f"{url}/{page}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    extract = data.get("extract", "")
                    
                    # Buscar menciones de Argentina, Mundial, etc.
                    if any(keyword in extract.lower() for keyword in ["argentina", "mundial", "selección", "messi"]):
                        events.append({
                            "date": date,
                            "type": "historical",
                            "priority": "low",
                            "source": "Wikipedia",
                            "description": f"Evento histórico de fútbol ({date_str})",
                            "details": extract[:200] + "..." if len(extract) > 200 else extract
                        })
            except:
                continue
        
        return events
    except Exception as e:
        print(f"⚠️  Error al obtener eventos de Wikipedia: {e}")
        return []


def get_events_calendar(date: str) -> List[Dict]:
    """Obtiene eventos del calendario (cumpleaños de jugadores, partidos, etc.)"""
    events = []

    birthdays = {
        "06-24": {"person": "Lionel Messi", "birth_year": 1987},
        "12-15": {"person": "Santiago Armando Rodríguez", "birth_year": 1983},
    }

    date_key = date[5:]  # MM-DD
    if date_key in birthdays:
        bday = birthdays[date_key]
        target_year = int(date[:4])
        age = target_year - bday["birth_year"]

        events.append({
            "date": date,
            "type": "birthday",
            "priority": "high",
            "person": bday["person"],
            "age": age,
            "description": f"Cumpleaños de {bday['person']} ({age} años)",
            "source": "calendario"
        })

    return events


def get_events_enhanced(date: str) -> List[Dict]:
    """Obtiene eventos desde múltiples fuentes"""
    all_events = []
    
    # 1. Archivo JSON (prioridad más alta)
    print("📅 Obteniendo eventos desde events.json...")
    json_events = get_events_from_json(date)
    all_events.extend(json_events)
    
    # 2. Calendario (cumpleaños, etc.)
    print("📅 Obteniendo eventos del calendario...")
    calendar_events = get_events_calendar(date)
    all_events.extend(calendar_events)
    
    # 3. Wikipedia (eventos históricos)
    print("📅 Obteniendo eventos históricos de Wikipedia...")
    wiki_events = get_events_wikipedia(date)
    all_events.extend(wiki_events)
    
    # 4. Scraper de eventos históricos (sitios configurados)
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from scrape_events import get_historical_events
        print("📅 Obteniendo eventos históricos con scraper...")
        scraped_events = get_historical_events(date)
        all_events.extend(scraped_events)
    except Exception as e:
        print(f"⚠️  Error al obtener eventos con scraper: {e}")
    
    # Eliminar duplicados
    seen = set()
    unique_events = []
    for event in all_events:
        key = (event.get("type"), event.get("description"))
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
    
    # Ordenar por prioridad
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    unique_events.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
    
    return unique_events


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Obtiene eventos del día desde múltiples fuentes"
    )
    parser.add_argument(
        "--date",
        help="Fecha en formato YYYY-MM-DD (default: hoy)",
        default=datetime.now().strftime("%Y-%m-%d")
    )
    parser.add_argument(
        "--output",
        help="Archivo JSON donde guardar (opcional)"
    )
    
    args = parser.parse_args()
    
    print(f"📅 Obteniendo eventos para {args.date}...")
    print("=" * 50)
    
    events = get_events_enhanced(args.date)
    
    if not events:
        print("   No hay eventos para esta fecha")
    else:
        print(f"   ✅ Encontrados {len(events)} evento(s):")
        for event in events:
            print(f"   - {event.get('type', 'unknown')}: {event.get('description', 'N/A')}")
            if event.get('source'):
                print(f"     Fuente: {event.get('source')}")
    
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

