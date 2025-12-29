#!/usr/bin/env python3
"""
Scraper mejorado de Wikipedia para eventos históricos de fútbol argentino
Usa páginas de fechas específicas (ej: "22 de junio") en lugar de anexos mensuales
Fase 4 - InforMessi
"""

import json
import os
import sys
import re
from datetime import datetime
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


def scrape_wikipedia_date_page(day: int, month: int) -> List[Dict]:
    """Scrapea eventos de una página de fecha específica (ej: '22 de junio')"""
    month_names = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    
    events = []
    page_name = f"{day}_de_{month_names[month]}"
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
        
        # Palabras clave PRIMARIAS (fútbol/Argentina - deben estar presentes)
        primary_keywords = [
            "selección argentina", "messi", "mundial de fútbol", "mundial de futbol",
            "copa américa", "albiceleste", "maradona", "escaloneta", "scaloni",
            "argentina.*fútbol", "argentina.*futbol", "argentina.*mundial",
            "argentina.*copa", "argentina.*selección"
        ]
        
        # Palabras clave SECUNDARIAS (fútbol relacionado)
        secondary_keywords = [
            "fútbol", "futbol", "fifa", "copa del mundo",
            "futbolista", "gol", "partido.*fútbol", "partido.*futbol",
            "campeonato.*fútbol", "campeonato.*futbol"
        ]
        
        # Buscar en todas las secciones
        for element in content.find_all(['li', 'p']):
            text = element.get_text(strip=True)
            
            if len(text) > 30:
                text_lower = text.lower()
                
                # Verificar palabras clave primarias (con regex para patrones)
                has_primary = False
                for kw in primary_keywords:
                    if "*" in kw:
                        # Patrón regex (ej: "argentina.*fútbol")
                        pattern = kw.replace("*", ".*")
                        if re.search(pattern, text_lower):
                            has_primary = True
                            break
                    elif kw in text_lower:
                        has_primary = True
                        break
                
                # Verificar palabras clave secundarias
                has_secondary = False
                for kw in secondary_keywords:
                    if "*" in kw:
                        pattern = kw.replace("*", ".*")
                        if re.search(pattern, text_lower):
                            has_secondary = True
                            break
                    elif kw in text_lower:
                        has_secondary = True
                        break
                
                # Contexto argentino/mundial/fútbol
                has_context = any(ctx in text_lower for ctx in [
                    "argentina", "mundial", "copa", "selección", 
                    "fútbol", "futbol", "fifa"
                ])
                
                # Filtrar: debe tener primaria, o (secundaria + contexto fuerte)
                if has_primary or (has_secondary and has_context):
                    # Excluir eventos que claramente no son de fútbol
                    exclude_keywords = [
                        "guerra", "batalla", "rey", "reina", "emperador",
                        "terremoto", "tsunami", "epidemia", "peste",
                        "revolución", "independencia", "declaración de guerra",
                        "fundación", "fundó", "se funda", "nace", "muere",
                        "matrimonio", "boda", "telefónica", "teléfono"
                    ]
                    
                    # Contexto fuerte de fútbol (si tiene esto, no excluir aunque tenga exclude_keywords)
                    strong_football_context = any(kw in text_lower for kw in [
                        "mundial de fútbol", "mundial de futbol", "copa del mundo",
                        "selección argentina", "selección de fútbol",
                        "maradona", "messi", "gol.*fútbol", "gol.*futbol",
                        "partido.*fútbol", "partido.*futbol", "copa américa",
                        "fifa", "futbolista", "jugador de fútbol"
                    ])
                    
                    # Si tiene palabras de exclusión y NO tiene contexto fuerte de fútbol, saltar
                    has_exclude = any(ekw in text_lower for ekw in exclude_keywords)
                    if has_exclude and not strong_football_context:
                        continue
                    
                    # Filtro adicional: debe mencionar explícitamente fútbol/Argentina en contexto deportivo
                    # Pero ser más flexible si tiene palabras clave fuertes
                    strong_football_keywords = [
                        "mundial", "copa américa", "maradona", "messi", 
                        "fifa", "selección argentina", "albiceleste"
                    ]
                    
                    has_strong_keyword = any(kw in text_lower for kw in strong_football_keywords)
                    
                    # Si tiene palabra clave fuerte, aceptar
                    # Si no, debe tener contexto claro de fútbol + Argentina
                    is_football_event = has_strong_keyword or (
                        has_secondary and "argentina" in text_lower
                    ) or (
                        "argentina" in text_lower and any(
                            re.search(pattern, text_lower) for pattern in [
                                r"argentina.*fútbol", r"argentina.*futbol", 
                                r"argentina.*mundial", r"argentina.*copa",
                                r"selección.*argentina"
                            ]
                        )
                    )
                    
                    if not is_football_event:
                        continue
                    
                    # Extraer año si está presente
                    year_match = re.search(r'\b(19|20)\d{2}\b', text)
                    year = year_match.group() if year_match else None
                    
                    # Formatear fecha (año 2026, mismo día/mes)
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
        
        return events
    except Exception as e:
        return []


def scrape_wikipedia_month_events(month: int) -> List[Dict]:
    """Scrapea eventos históricos de un mes desde páginas de fechas específicas"""
    all_events = []
    
    month_names = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    
    print(f"   Scrapeando días del mes {month_names[month]}...")
    
    # Scrapear días conocidos con eventos importantes (optimización)
    # Días importantes: 22 (gol de Maradona), 18 (finales), 11 (inicios), etc.
    important_days = [1, 11, 13, 18, 22, 25, 30]  # Días con más probabilidad de eventos
    
    # También scrapear algunos días aleatorios
    import random
    random_days = random.sample(range(1, 29), 5)  # 5 días aleatorios
    
    days_to_scrape = sorted(set(important_days + random_days))
    
    events_found = 0
    for day in days_to_scrape:
        try:
            events = scrape_wikipedia_date_page(day, month)
            if events:
                all_events.extend(events)
                events_found += len(events)
                print(f"      Día {day}: {len(events)} evento(s)")
        except Exception as e:
            continue
    
    if events_found == 0:
        # Si no encontramos nada en días importantes, probar más días
        print(f"   No se encontraron eventos en días importantes, probando más días...")
        for day in range(1, 29):
            if day not in days_to_scrape:
                try:
                    events = scrape_wikipedia_date_page(day, month)
                    if events:
                        all_events.extend(events)
                        events_found += len(events)
                        if events_found >= 10:  # Limitar para no hacer demasiadas requests
                            break
                except:
                    continue
    
    return all_events


def scrape_all_wikipedia_events() -> Dict[str, List[Dict]]:
    """Scrapea eventos históricos de todos los meses"""
    all_events = {}
    
    print("📅 Scrapeando eventos históricos de Wikipedia...")
    print("   Usando páginas de fechas específicas (ej: '22 de junio')")
    print("   Esto puede tardar varios minutos...")
    print()
    
    for month in range(1, 13):
        print(f"📅 Mes {month}/12...", end=" ", flush=True)
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
        description="Scrapea eventos históricos de Wikipedia desde páginas de fechas específicas"
    )
    parser.add_argument(
        "--month",
        type=int,
        help="Mes específico a scrapear (1-12), si no se especifica scrapea todos"
    )
    parser.add_argument(
        "--day",
        type=int,
        help="Día específico a scrapear (1-31), requiere --month"
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
    
    if args.day and args.month:
        # Scrapear día específico
        print(f"📅 Scrapeando eventos del {args.day} de {args.month}...")
        events = scrape_wikipedia_date_page(args.day, args.month)
        events_by_date = {}
        for event in events:
            date = event["date"]
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].append(event)
    elif args.month:
        # Scrapear mes específico
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
            for event in events[:2]:
                print(f"      - {event['description'][:60]}...")
    else:
        # Guardar eventos
        formatted_events = save_events_to_json(events_by_date, args.output)
        
        if args.merge:
            merge_with_existing_events(formatted_events)


if __name__ == "__main__":
    main()

