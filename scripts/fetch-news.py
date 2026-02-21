#!/usr/bin/env python3
"""
Script para obtener noticias deportivas de Argentina
Fase 4 - InforMessi
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import quote

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Necesitas instalar dependencias:")
    print("  pip install requests beautifulsoup4 feedparser")
    sys.exit(1)

try:
    import feedparser
except ImportError:
    feedparser = None
    print("⚠️  feedparser no instalado, solo se usará scraping")


def _validate_news_basic(news_list: List[Dict], max_days: int = 3, reference_date: Optional[str] = None) -> List[Dict]:
    """Validación básica de noticias (fecha y contenido obsoleto)"""
    valid_news = []
    if reference_date:
        try:
            today = datetime.strptime(reference_date, "%Y-%m-%d").date()
        except Exception:
            today = datetime.now().date()
    else:
        today = datetime.now().date()
    
    # Palabras clave que indican información obsoleta
    obsolete_keywords = [
        "gerardo martino", "tata martino", "sampaoli", "bauza",
        "maradona dt", "batista", "sabella"
    ]
    
    # Contextos donde estas palabras son válidas (históricos)
    valid_contexts = [
        "histórico", "historia", "recordó", "recordar", 
        "pasado", "anteriormente", "en el pasado"
    ]
    
    for news in news_list:
        # Validar fecha
        published_at = news.get("published_at", "")
        if published_at:
            try:
                if "T" in published_at:
                    date_str = published_at.split("T")[0]
                    news_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    days_diff = (today - news_date).days
                    if days_diff > max_days:
                        continue
                else:
                    # Intentar otros formatos
                    news_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    days_diff = (today - news_date.date()).days
                    if days_diff > max_days:
                        continue
            except Exception:
                # Si no se puede parsear, asumir reciente (mejor incluir que excluir)
                pass
        
        # Validar contenido obsoleto
        title = news.get("title", "").lower()
        description = news.get("description", "").lower()
        text = f"{title} {description}"
        
        # Buscar palabras clave obsoletas
        has_obsolete = False
        for keyword in obsolete_keywords:
            if keyword in text:
                # Verificar si está en contexto histórico válido
                is_historical = any(context in text for context in valid_contexts)
                if not is_historical:
                    has_obsolete = True
                    break
        
        if has_obsolete:
            continue
        
        valid_news.append(news)
    
    return valid_news


def get_news_newsapi(api_key: str, max_results: int = 5, silent: bool = False) -> List[Dict]:
    """Obtiene noticias de NewsAPI relacionadas con selección argentina y mundial 2026"""
    
    # Queries específicas para selección argentina y mundial
    queries = [
        "Argentina selección fútbol mundial 2026",
        "Selección Argentina mundial",
        "Argentina Messi mundial 2026",
        "Scaloni Argentina mundial"
    ]
    
    all_news = []
    
    for query in queries[:2]:  # Usar solo las 2 primeras para no exceder límites
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "language": "es",
                "sortBy": "publishedAt",
                "pageSize": 3,  # Menos por query para tener variedad
                "apiKey": api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for article in data.get("articles", []):
                # Filtrar por palabras clave relevantes
                title = article.get("title", "").lower()
                description = article.get("description", "").lower()
                
                keywords = ["argentina", "selección", "messi", "mundial", "2026", 
                           "scaloni", "albiceleste", "afa", "copamérica"]
                
                if any(keyword in title or keyword in description for keyword in keywords):
                    # Evitar duplicados
                    url_article = article.get("url", "")
                    if not any(item['url'] == url_article for item in all_news):
                        all_news.append({
                            "title": article.get("title", ""),
                            "description": article.get("description", "")[:200],
                            "url": url_article,
                            "source": article.get("source", {}).get("name", "NewsAPI"),
                            "published_at": article.get("publishedAt", "")
                        })
                        
                        if len(all_news) >= max_results:
                            break
            
            if len(all_news) >= max_results:
                break
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if not silent:
                    print(f"⚠️  Límite de NewsAPI alcanzado, usando otras fuentes")
                break
            else:
                if not silent:
                    print(f"⚠️  Error HTTP de NewsAPI: {e}")
                break
        except requests.exceptions.RequestException as e:
            if not silent:
                print(f"⚠️  Error al obtener noticias de NewsAPI: {e}")
            break
    
    return all_news[:max_results]


def get_news_rss(url: str, max_results: int = 5, silent: bool = False) -> List[Dict]:
    """Obtiene noticias de un feed RSS"""
    if not feedparser:
        return []
    
    try:
        feed = feedparser.parse(url)
        
        # Verificar si el feed es válido
        if feed.bozo and feed.bozo_exception:
            if not silent:
                print(f"⚠️  Feed RSS inválido o no disponible: {url}")
            return []
        
        if not feed.entries:
            if not silent:
                print(f"⚠️  Feed RSS vacío: {url}")
            return []
        
        news = []
        
        for entry in feed.entries[:max_results]:
            # Filtrar solo noticias de fútbol/Argentina
            title = entry.get("title", "").lower()
            description = entry.get("description", "").lower()
            
            # Palabras clave relevantes
            keywords = ["argentina", "selección", "messi", "mundial", "fútbol", "futbol", 
                       "scaloni", "afa", "albiceleste", "copamérica", "copa américa"]
            
            if any(keyword in title or keyword in description for keyword in keywords):
                # Extraer fecha
                published = entry.get("published", "")
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    from time import mktime
                    published = datetime.fromtimestamp(mktime(entry.published_parsed)).isoformat()
                
                news.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("description", "")[:200],  # Limitar descripción
                    "url": entry.get("link", ""),
                    "source": feed.feed.get("title", "RSS Feed"),
                    "published_at": published
                })
        
        return news
    except Exception as e:
        if not silent:
            print(f"⚠️  Error al obtener RSS de {url}: {e}")
        return []


def get_news_tyc_sports(max_results: int = 5) -> List[Dict]:
    """Obtiene noticias de TyC Sports (scraping mejorado)"""
    try:
        # Intentar página principal de fútbol
        urls_to_try = [
            "https://www.tycsports.com/futbol",
            "https://www.tycsports.com",
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        news = []
        
        for url in urls_to_try:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar enlaces con palabras clave de fútbol/Argentina
                keywords = ["argentina", "selección", "messi", "mundial", "fútbol", "futbol"]
                
                # Buscar todos los enlaces
                links = soup.find_all('a', href=True)
                
                for link in links:
                    if len(news) >= max_results:
                        break
                    
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # Filtrar por palabras clave y longitud mínima
                    if title and len(title) > 20 and any(kw in title.lower() for kw in keywords):
                        # Construir URL completa
                        if href.startswith('/'):
                            full_url = f"https://www.tycsports.com{href}"
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                        
                        # Evitar duplicados
                        if not any(item['url'] == full_url for item in news):
                            news.append({
                                "title": title[:100],  # Limitar longitud
                                "description": "",
                                "url": full_url,
                                "source": "TyC Sports",
                                "published_at": datetime.now().isoformat()
                            })
                
                if news:
                    break  # Si encontramos noticias, no probar otras URLs
                    
            except Exception as e:
                continue
        
        return news[:max_results]
    except Exception as e:
        # No imprimir en modo silencioso (se maneja desde get_news_argentina)
        return []


def get_news_argentina(max_results: int = 5, silent: bool = False, reference_date: Optional[str] = None, max_days: int = 3) -> List[Dict]:
    """Obtiene noticias deportivas de Argentina desde múltiples fuentes"""
    
    all_news = []
    
    # 1. NewsAPI (si está configurado) - Prioridad alta
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if newsapi_key:
        if not silent:
            print("📰 Obteniendo noticias de NewsAPI (selección argentina, mundial 2026)...")
        news = get_news_newsapi(newsapi_key, max_results, silent=silent)
        if news:
            all_news.extend(news)
            if not silent:
                print(f"   ✅ {len(news)} noticia(s) de NewsAPI")
    
    # 2. RSS Feeds (gratis, sin API key)
    rss_feeds = [
        "https://www.tycsports.com/rss.xml",  # TyC Sports RSS principal
        "https://www.ole.com.ar/rss/ultimas-noticias.xml",  # Olé
        # Agregar más feeds si están disponibles
    ]
    
    for feed_url in rss_feeds:
        try:
            if not silent:
                print(f"📰 Obteniendo noticias de RSS: {feed_url}...")
            news = get_news_rss(feed_url, max_results, silent=silent)
            if news:
                all_news.extend(news)
                if not silent:
                    print(f"   ✅ {len(news)} noticia(s) obtenida(s)")
        except Exception as e:
            if not silent:
                print(f"   ⚠️  Error con {feed_url}: {e}")
            continue
    
    # 3. Scraping (fallback)
    if not all_news:
        if not silent:
            print("📰 Obteniendo noticias de TyC Sports (scraping)...")
        news = get_news_tyc_sports(max_results)
        all_news.extend(news)
    
    # Filtrar duplicados y ordenar por fecha
    seen_titles = set()
    unique_news = []
    for item in all_news:
        title_lower = item["title"].lower()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_news.append(item)
    
    # Validar noticias (fecha y contenido obsoleto)
    validated_news = _validate_news_basic(unique_news, max_days=max_days, reference_date=reference_date)
    
    # Limitar resultados
    return validated_news[:max_results]


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Obtiene noticias deportivas para InforMessi"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Número máximo de noticias (default: 5)"
    )
    parser.add_argument(
        "--output",
        help="Archivo JSON donde guardar (opcional)"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Solo imprimir JSON (para uso en scripts)"
    )
    parser.add_argument(
        "--date",
        help="Fecha de referencia para filtrar noticias (YYYY-MM-DD)",
        default=None
    )
    parser.add_argument(
        "--max-days",
        type=int,
        default=3,
        help="Ventana en días hacia atrás desde la fecha de referencia (default: 3)"
    )
    
    args = parser.parse_args()
    
    if not args.json_only:
        print("📰 Obteniendo noticias deportivas...")
        print("=" * 50)
    
    news = get_news_argentina(
        args.max_results,
        silent=args.json_only,
        reference_date=args.date,
        max_days=args.max_days
    )
    
    if args.json_only:
        # Solo imprimir JSON (para uso en scripts)
        print(json.dumps(news, ensure_ascii=False))
    else:
        # Modo interactivo con información
        if not news:
            print("   ⚠️  No se obtuvieron noticias")
        else:
            print(f"   ✅ Encontradas {len(news)} noticia(s):")
            for i, item in enumerate(news, 1):
                print(f"   {i}. {item['title'][:60]}...")
                print(f"      Fuente: {item['source']}")
        
        # Guardar si se especificó output
        if args.output:
            output_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "news": news
            }
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Datos guardados en: {args.output}")
        
        # Retornar JSON para uso en scripts (al final)
        print(json.dumps(news, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

