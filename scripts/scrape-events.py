#!/usr/bin/env python3
"""
Scraper genérico para eventos históricos de fútbol
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
    print("ERROR: Necesitas instalar 'requests' y 'beautifulsoup4'")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent


def scrape_wikipedia_football_events(date: str) -> List[Dict]:
    """Scrapea eventos históricos de fútbol desde Wikipedia"""
    try:
        day = datetime.strptime(date, "%Y-%m-%d").day
        month = datetime.strptime(date, "%Y-%m-%d").month
        
        month_names = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        
        # Páginas de Wikipedia relevantes
        pages = [
            f"Anexo:Hechos_relevantes_de_{month_names[month]}_en_el_fútbol",
            f"{day}_de_{month_names[month]}_en_el_fútbol",
        ]
        
        events = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        for page in pages:
            try:
                url = f"https://es.wikipedia.org/wiki/{page}"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar eventos relacionados con Argentina
                content = soup.find('div', {'id': 'mw-content-text'})
                if not content:
                    continue
                
                # Buscar listas y párrafos
                for element in content.find_all(['li', 'p']):
                    text = element.get_text(strip=True)
                    
                    # Filtrar por palabras clave argentinas
                    keywords = ["argentina", "selección argentina", "messi", "mundial", 
                               "copa américa", "albiceleste", "afa"]
                    
                    if any(keyword in text.lower() for keyword in keywords) and len(text) > 30:
                        # Extraer año si está presente
                        import re
                        year_match = re.search(r'\b(19|20)\d{2}\b', text)
                        year = year_match.group() if year_match else None
                        
                        events.append({
                            "date": date,
                            "type": "historical",
                            "priority": "low",
                            "description": text[:200],  # Limitar longitud
                            "year": year,
                            "source": "Wikipedia",
                            "url": url
                        })
                        
                        if len(events) >= 5:  # Limitar eventos por fuente
                            break
                            
            except Exception as e:
                continue
        
        return events
    except Exception as e:
        print(f"⚠️  Error al scrapear Wikipedia: {e}")
        return []


def scrape_custom_site(url: str, selectors: Dict, date: str) -> List[Dict]:
    """
    Scraper genérico para sitios personalizados
    
    selectors: {
        "container": "div.article",  # Selector del contenedor
        "title": "h2",              # Selector del título
        "description": "p",          # Selector de la descripción
        "date": ".date"              # Selector de la fecha (opcional)
    }
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        events = []
        
        # Buscar contenedores
        containers = soup.select(selectors.get("container", "article"))
        
        for container in containers[:10]:  # Limitar a 10
            try:
                title_elem = container.select_one(selectors.get("title", "h2, h3"))
                desc_elem = container.select_one(selectors.get("description", "p"))
                date_elem = container.select_one(selectors.get("date", ""))
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Filtrar por palabras clave relevantes
                    text = f"{title} {description}".lower()
                    keywords = ["argentina", "selección", "messi", "mundial", "fútbol", "futbol"]
                    
                    if any(keyword in text for keyword in keywords):
                        events.append({
                            "date": date,
                            "type": "historical",
                            "priority": "low",
                            "description": f"{title}. {description[:150]}",
                            "source": url,
                            "url": url
                        })
            except Exception:
                continue
        
        return events
    except Exception as e:
        print(f"⚠️  Error al scrapear {url}: {e}")
        return []


def scrape_events_from_config(date: str, config_file: str = "scrape-config.json") -> List[Dict]:
    """Scrapea eventos desde sitios configurados en un archivo JSON"""
    config_path = PROJECT_ROOT / "data" / config_file
    
    if not config_path.exists():
        return []
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        all_events = []
        
        # Scrapear cada sitio configurado
        for site in config.get("sites", []):
            url = site.get("url")
            selectors = site.get("selectors", {})
            enabled = site.get("enabled", True)
            
            if not enabled or not url:
                continue
            
            print(f"📅 Scrapeando: {url}...")
            events = scrape_custom_site(url, selectors, date)
            all_events.extend(events)
        
        return all_events
    except Exception as e:
        print(f"⚠️  Error al leer configuración: {e}")
        return []


def get_historical_events(date: str) -> List[Dict]:
    """Obtiene eventos históricos desde múltiples fuentes"""
    all_events = []
    
    # 1. Wikipedia (automático)
    print("📅 Obteniendo eventos históricos de Wikipedia...")
    wiki_events = scrape_wikipedia_football_events(date)
    all_events.extend(wiki_events)
    
    # 2. Sitios configurados (si existe config)
    config_events = scrape_events_from_config(date)
    all_events.extend(config_events)
    
    # Eliminar duplicados
    seen = set()
    unique_events = []
    for event in all_events:
        key = event.get("description", "")[:50]
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
    
    return unique_events


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scrapea eventos históricos de fútbol"
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
    parser.add_argument(
        "--url",
        help="URL personalizada para scrapear"
    )
    parser.add_argument(
        "--container",
        help="Selector CSS del contenedor (ej: 'div.article')"
    )
    parser.add_argument(
        "--title",
        help="Selector CSS del título (ej: 'h2')"
    )
    
    args = parser.parse_args()
    
    print(f"📅 Obteniendo eventos históricos para {args.date}...")
    print("=" * 50)
    
    if args.url:
        # Scrapear URL personalizada
        selectors = {
            "container": args.container or "article",
            "title": args.title or "h2, h3",
            "description": "p"
        }
        events = scrape_custom_site(args.url, selectors, args.date)
    else:
        # Obtener eventos históricos automáticos
        events = get_historical_events(args.date)
    
    if not events:
        print("   No se encontraron eventos históricos")
    else:
        print(f"   ✅ Encontrados {len(events)} evento(s):")
        for event in events[:5]:
            print(f"   - {event['description'][:60]}...")
    
    # Guardar si se especificó output
    if args.output:
        output_data = {
            "date": args.date,
            "events": events
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Datos guardados en: {args.output}")
    
    # Retornar JSON
    print(json.dumps(events, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

