#!/usr/bin/env python3
"""
Scraper de Wikipedia para eventos históricos de fútbol argentino
Extrae eventos y los formatea para agregar a events.json
Fase 4 - InforMessi
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Necesitas instalar 'requests' y 'beautifulsoup4'")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def scrape_wikipedia_month_events(month: int) -> List[Dict]:
    """Scrapea todos los eventos históricos de un mes desde Wikipedia"""
    month_names = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    
    events = []
    page_name = f"Anexo:Hechos_relevantes_de_{month_names[month]}_en_el_fútbol"
    url = f"https://es.wikipedia.org/wiki/{page_name}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find('div', {'id': 'mw-content-text'})
        if not content:
            return events
        
        # Buscar todos los días del mes en listas y secciones
        current_day = None
        
        # Buscar secciones por día (h2, h3 con números)
        for heading in content.find_all(['h2', 'h3']):
            heading_text = heading.get_text(strip=True)
            day_match = re.search(r'^(\d{1,2})\s+de\s+', heading_text, re.IGNORECASE)
            if day_match:
                try:
                    current_day = int(day_match.group(1))
                except:
                    continue
        
        # Si no encontramos días en headings, buscar en listas
        if current_day is None:
            for li in content.find_all('li'):
                text = li.get_text(strip=True)
                day_match = re.search(r'^(\d{1,2})\s+de\s+', text, re.IGNORECASE)
                if day_match:
                    try:
                        current_day = int(day_match.group(1))
                    except:
                        continue
                    # Procesar este elemento
                    if len(text) > 30:
                        # Filtrar por palabras clave argentinas/mundialistas
                        keywords = [
                            "argentina", "selección argentina", "messi", "mundial",
                            "copa américa", "albiceleste", "afa", "maradona",
                            "escaloneta", "scaloni", "qatar", "brasil", "alemania",
                            "francia", "españa", "inglaterra", "fútbol", "futbol"
                        ]
                        
                        text_lower = text.lower()
                        if any(keyword in text_lower for keyword in keywords):
                            # Extraer año si está presente
                            year_match = re.search(r'\b(19|20)\d{2}\b', text)
                            year = year_match.group() if year_match else None
                            
                            # Formatear fecha (usar año del Mundial 2026, mismo día/mes)
                            event_date = f"2026-{month:02d}-{current_day:02d}"
                            
                            events.append({
                                "date": event_date,
                                "type": "historical",
                                "priority": "low",
                                "description": text[:200],
                                "historical_year": year,
                                "source": "Wikipedia",
                                "url": url,
                                "day": current_day,
                                "month": month
                            })
        
        # También buscar en párrafos y listas sin estructura de días
        for element in content.find_all(['li', 'p']):
            text = element.get_text(strip=True)
            
            if len(text) > 30:
                keywords = [
                    "argentina", "selección argentina", "messi", "mundial",
                    "copa américa", "albiceleste", "afa", "maradona"
                ]
                
                text_lower = text.lower()
                if any(keyword in text_lower for keyword in keywords):
                    # Intentar extraer día del contexto
                    day_match = re.search(r'\b(\d{1,2})\s+de\s+', text, re.IGNORECASE)
                    if day_match:
                        try:
                            day = int(day_match.group(1))
                            if 1 <= day <= 31:
                                year_match = re.search(r'\b(19|20)\d{2}\b', text)
                                year = year_match.group() if year_match else None
                                
                                event_date = f"2026-{month:02d}-{day:02d}"
                                
                                events.append({
                                    "date": event_date,
                                    "type": "historical",
                                    "priority": "low",
                                    "description": text[:200],
                                    "historical_year": year,
                                    "source": "Wikipedia",
                                    "url": url,
                                    "day": day,
                                    "month": month
                                })
                        except:
                            pass
        
        return events
    except Exception as e:
        print(f"⚠️  Error al scrapear Wikipedia: {e}")
        return []


def scrape_all_wikipedia_events() -> Dict[str, List[Dict]]:
    """Scrapea eventos históricos de todos los meses"""
    all_events = {}
    
    print("📅 Scrapeando eventos históricos de Wikipedia...")
    print("   Esto puede tardar varios minutos...")
    print()
    
    for month in range(1, 13):
        print(f"   Mes {month}/12...", end=" ", flush=True)
        events = scrape_wikipedia_month_events(month)
        
        # Agrupar por fecha
        for event in events:
            date_key = event["date"]
            if date_key not in all_events:
                all_events[date_key] = []
            all_events[date_key].append(event)
        
        print(f"✅ {len(events)} eventos encontrados")
    
    return all_events


def save_events_to_json(events_by_date: Dict[str, List[Dict]], output_file: str = "events-wikipedia.json"):
    """Guarda eventos en formato compatible con events.json"""
    output_path = DATA_DIR / output_file
    
    # Cargar eventos existentes si hay
    existing_events = []
    events_file = DATA_DIR / "events.json"
    if events_file.exists():
        with open(events_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            existing_events = data.get("events", [])
    
    # Convertir eventos de Wikipedia al formato de events.json
    formatted_events = []
    for date, events in events_by_date.items():
        for event in events:
            # Verificar si ya existe (evitar duplicados)
            existing = any(
                e.get("date") == date and 
                e.get("description", "")[:50] == event["description"][:50]
                for e in existing_events
            )
            
            if not existing:
                formatted_events.append({
                    "date": date,
                    "type": "historical",
                    "priority": "low",
                    "description": event["description"],
                    "historical_year": event.get("historical_year"),
                    "source": "Wikipedia",
                    "url": event.get("url", "")
                })
    
    # Guardar en archivo separado
    output_data = {
        "description": "Eventos históricos scrapeados de Wikipedia",
        "schema_version": "1.0",
        "events": formatted_events,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_events": len(formatted_events)
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Eventos guardados en: {output_path}")
    print(f"   Total: {len(formatted_events)} eventos")
    
    return formatted_events


def merge_with_existing_events(new_events: List[Dict]):
    """Fusiona eventos de Wikipedia con events.json existente"""
    events_file = DATA_DIR / "events.json"
    
    if events_file.exists():
        with open(events_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "description": "Eventos del día para InforMessi",
            "schema_version": "1.0",
            "events": []
        }
    
    existing_events = data.get("events", [])
    
    # Agregar nuevos eventos (evitar duplicados)
    for new_event in new_events:
        # Verificar duplicados
        is_duplicate = any(
            e.get("date") == new_event["date"] and
            e.get("description", "")[:50] == new_event["description"][:50]
            for e in existing_events
        )
        
        if not is_duplicate:
            existing_events.append(new_event)
    
    data["events"] = existing_events
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Guardar
    with open(events_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Eventos fusionados con events.json")
    print(f"   Total en events.json: {len(existing_events)} eventos")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scrapea eventos históricos de Wikipedia y los agrega a events.json"
    )
    parser.add_argument(
        "--month",
        type=int,
        help="Mes específico a scrapear (1-12), si no se especifica scrapea todos"
    )
    parser.add_argument(
        "--output",
        default="events-wikipedia.json",
        help="Archivo de salida (default: events-wikipedia.json)"
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Fusionar eventos con events.json existente"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo mostrar eventos sin guardar"
    )
    
    args = parser.parse_args()
    
    if args.month:
        # Scrapear solo un mes
        print(f"📅 Scrapeando eventos del mes {args.month}...")
        events = scrape_wikipedia_month_events(args.month)
        events_by_date = {}
        for event in events:
            date = event["date"]
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].append(event)
    else:
        # Scrapear todos los meses
        events_by_date = scrape_all_wikipedia_events()
    
    if args.dry_run:
        print("\n📋 Eventos encontrados (dry-run, no guardados):")
        total = sum(len(events) for events in events_by_date.values())
        print(f"   Total: {total} eventos en {len(events_by_date)} fechas")
        for date, events in sorted(events_by_date.items())[:10]:
            print(f"   {date}: {len(events)} evento(s)")
    else:
        # Guardar eventos
        formatted_events = save_events_to_json(events_by_date, args.output)
        
        if args.merge:
            merge_with_existing_events(formatted_events)


if __name__ == "__main__":
    main()

