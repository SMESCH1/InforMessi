#!/usr/bin/env python3
"""
Script para obtener noticias deportivas de Argentina y fútbol mundial
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


# --- Keywords ---

# Keywords estrechos: foco en selección argentina
KEYWORDS_NARROW = [
    "argentina", "selección", "messi", "mundial", "2026",
    "scaloni", "albiceleste", "afa", "copamérica", "copa américa"
]

# Keywords amplios: fútbol mundial, liga argentina, otras selecciones
KEYWORDS_BROAD = [
    "argentina", "selección", "messi", "mundial", "2026",
    "scaloni", "albiceleste", "afa",
    "world cup", "copa del mundo", "fifa",
    "liga profesional", "superliga", "primera división",
    "eliminatorias", "conmebol",
    "fútbol", "futbol", "football",
    "copa américa", "champions", "libertadores",
]

# --- NewsAPI Queries ---

NEWSAPI_QUERIES_NARROW = [
    "Argentina selección fútbol mundial 2026",
    "Selección Argentina mundial",
]

NEWSAPI_QUERIES_BROAD = [
    "Selección Argentina mundial 2026",
    "Mundial 2026 fútbol",
    "Liga Profesional Argentina fútbol",
    "FIFA World Cup 2026",
]

# --- RSS Feeds ---

RSS_FEEDS_DEFAULT = [
    "https://www.tycsports.com/rss.xml",
    "https://www.ole.com.ar/rss/ultimas-noticias.xml",
]

RSS_FEEDS_BROAD = [
    "https://www.tycsports.com/rss.xml",
    "https://www.ole.com.ar/rss/ultimas-noticias.xml",
    "https://www.espn.com.ar/rss/futbol/nota",
    "https://www.marca.com/rss/futbol.xml",
    "https://www.goal.com/feeds/es/news",
]


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

    obsolete_keywords = [
        "gerardo martino", "tata martino", "sampaoli", "bauza",
        "maradona dt", "batista", "sabella"
    ]

    valid_contexts = [
        "histórico", "historia", "recordó", "recordar",
        "pasado", "anteriormente", "en el pasado"
    ]

    for news in news_list:
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
                    news_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    days_diff = (today - news_date.date()).days
                    if days_diff > max_days:
                        continue
            except Exception:
                pass

        title = news.get("title", "").lower()
        description = news.get("description", "").lower()
        text = f"{title} {description}"

        has_obsolete = False
        for keyword in obsolete_keywords:
            if keyword in text:
                is_historical = any(context in text for context in valid_contexts)
                if not is_historical:
                    has_obsolete = True
                    break

        if has_obsolete:
            continue

        valid_news.append(news)

    return valid_news


def get_news_newsapi(api_key: str, max_results: int = 8, silent: bool = False, broad: bool = False) -> List[Dict]:
    """Obtiene noticias de NewsAPI"""

    queries = NEWSAPI_QUERIES_BROAD if broad else NEWSAPI_QUERIES_NARROW
    keywords = KEYWORDS_BROAD if broad else KEYWORDS_NARROW
    num_queries = 3 if broad else 2

    all_news = []

    for query in queries[:num_queries]:
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "language": "es",
                "sortBy": "publishedAt",
                "pageSize": 3,
                "apiKey": api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for article in data.get("articles", []):
                title = article.get("title", "").lower()
                description = article.get("description", "").lower()

                if any(kw in title or kw in description for kw in keywords):
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
                    print("⚠️  Límite de NewsAPI alcanzado, usando otras fuentes")
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


def get_news_rss(url: str, max_results: int = 8, silent: bool = False, broad: bool = False) -> List[Dict]:
    """Obtiene noticias de un feed RSS"""
    if not feedparser:
        return []

    try:
        feed = feedparser.parse(url)

        if feed.bozo and feed.bozo_exception:
            if not silent:
                print(f"⚠️  Feed RSS inválido o no disponible: {url}")
            return []

        if not feed.entries:
            if not silent:
                print(f"⚠️  Feed RSS vacío: {url}")
            return []

        keywords = KEYWORDS_BROAD if broad else KEYWORDS_NARROW
        news = []

        for entry in feed.entries[:max_results * 3]:  # Leer más para filtrar
            title = entry.get("title", "").lower()
            description = entry.get("description", "").lower()

            if any(kw in title or kw in description for kw in keywords):
                published = entry.get("published", "")
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    from time import mktime
                    published = datetime.fromtimestamp(mktime(entry.published_parsed)).isoformat()

                news.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("description", "")[:200],
                    "url": entry.get("link", ""),
                    "source": feed.feed.get("title", "RSS Feed"),
                    "published_at": published
                })

                if len(news) >= max_results:
                    break

        return news
    except Exception as e:
        if not silent:
            print(f"⚠️  Error al obtener RSS de {url}: {e}")
        return []


def get_news_tyc_sports(max_results: int = 8) -> List[Dict]:
    """Obtiene noticias de TyC Sports (scraping mejorado)"""
    try:
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

                keywords = ["argentina", "selección", "messi", "mundial", "fútbol", "futbol"]

                links = soup.find_all('a', href=True)

                for link in links:
                    if len(news) >= max_results:
                        break

                    title = link.get_text(strip=True)
                    href = link.get('href', '')

                    if title and len(title) > 20 and any(kw in title.lower() for kw in keywords):
                        if href.startswith('/'):
                            full_url = f"https://www.tycsports.com{href}"
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue

                        if not any(item['url'] == full_url for item in news):
                            news.append({
                                "title": title[:100],
                                "description": "",
                                "url": full_url,
                                "source": "TyC Sports",
                                "published_at": datetime.now().isoformat()
                            })

                if news:
                    break

            except Exception:
                continue

        return news[:max_results]
    except Exception:
        return []


def get_news_argentina(max_results: int = 8, silent: bool = False, reference_date: Optional[str] = None, max_days: int = 3, broad: bool = False) -> List[Dict]:
    """Obtiene noticias deportivas desde múltiples fuentes"""

    all_news = []

    # 1. NewsAPI (si está configurado)
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if newsapi_key:
        if not silent:
            print("📰 Obteniendo noticias de NewsAPI...")
        news = get_news_newsapi(newsapi_key, max_results, silent=silent, broad=broad)
        if news:
            all_news.extend(news)
            if not silent:
                print(f"   ✅ {len(news)} noticia(s) de NewsAPI")

    # 2. RSS Feeds
    rss_feeds = RSS_FEEDS_BROAD if broad else RSS_FEEDS_DEFAULT

    for feed_url in rss_feeds:
        try:
            if not silent:
                print(f"📰 Obteniendo noticias de RSS: {feed_url}...")
            news = get_news_rss(feed_url, max_results, silent=silent, broad=broad)
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

    # Deduplicar por título
    seen_titles = set()
    unique_news = []
    for item in all_news:
        title_lower = item["title"].lower().strip()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_news.append(item)

    # Validar noticias
    validated_news = _validate_news_basic(unique_news, max_days=max_days, reference_date=reference_date)

    return validated_news[:max_results]


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Obtiene noticias deportivas para InforMessi"
    )
    parser.add_argument(
        "--max-results", type=int, default=8,
        help="Número máximo de noticias (default: 8)"
    )
    parser.add_argument("--output", help="Archivo JSON donde guardar (opcional)")
    parser.add_argument(
        "--json-only", action="store_true",
        help="Solo imprimir JSON (para uso en scripts)"
    )
    parser.add_argument(
        "--date", help="Fecha de referencia para filtrar noticias (YYYY-MM-DD)",
        default=None
    )
    parser.add_argument(
        "--max-days", type=int, default=3,
        help="Ventana en días hacia atrás (default: 3)"
    )
    parser.add_argument(
        "--broad", action="store_true",
        help="Usar keywords amplios (fútbol mundial, liga argentina, FIFA, etc.)"
    )

    args = parser.parse_args()

    if not args.json_only:
        mode = "amplio" if args.broad else "estándar"
        print(f"📰 Obteniendo noticias deportivas (modo {mode})...")
        print("=" * 50)

    news = get_news_argentina(
        args.max_results,
        silent=args.json_only,
        reference_date=args.date,
        max_days=args.max_days,
        broad=args.broad,
    )

    if args.json_only:
        print(json.dumps(news, ensure_ascii=False))
    else:
        if not news:
            print("   ⚠️  No se obtuvieron noticias")
        else:
            print(f"   ✅ Encontradas {len(news)} noticia(s):")
            for i, item in enumerate(news, 1):
                print(f"   {i}. {item['title'][:60]}...")
                print(f"      Fuente: {item['source']}")

        if args.output:
            output_data = {"date": datetime.now().strftime("%Y-%m-%d"), "news": news}
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Datos guardados en: {args.output}")

        print(json.dumps(news, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
