#!/usr/bin/env python3
"""
Scraper diario de noticias deportivas para InforMessi.
Se ejecuta a la madrugada vía GitHub Actions.
Guarda noticias en data/daily-news/YYYY-MM-DD.json.
"""

import json
import logging
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from time_utils import now_ar_iso, today_ar
from importlib import import_module

_fetch_news = import_module("fetch-news")
filter_news_llm = _fetch_news.filter_news_llm

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DAILY_NEWS_DIR = PROJECT_ROOT / "data" / "daily-news"
DAILY_NEWS_DIR.mkdir(parents=True, exist_ok=True)

_SUBPROC_ENV = {**os.environ, "PYTHONUTF8": "1"}


def _categorize_news(news_item):
    """Clasifica una noticia por categoría."""
    title = (news_item.get("title", "") or "").lower()
    desc = (news_item.get("description", "") or "").lower()
    text = f"{title} {desc}"

    seleccion_kw = ["argentina", "selección", "messi", "scaloni", "albiceleste", "afa", "scaloneta"]
    mundial_kw = ["mundial", "world cup", "2026", "fifa", "copa del mundo"]
    liga_kw = ["liga profesional", "superliga", "primera división", "boca", "river",
               "racing", "independiente", "san lorenzo", "huracán"]

    if any(kw in text for kw in seleccion_kw):
        return "seleccion"
    if any(kw in text for kw in mundial_kw):
        return "mundial"
    if any(kw in text for kw in liga_kw):
        return "liga"
    return "general"


def scrape_news(target_date: str) -> list:
    """Ejecuta fetch-news.py con modo broad y retorna las noticias."""
    logger.info("📰 Ejecutando fetch-news.py --broad...")

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "fetch-news.py"),
        "--broad",
        "--max-results", "10",
        "--date", target_date,
        "--max-days", "2",
        "--json-only",
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60,
            env=_SUBPROC_ENV, encoding="utf-8",
        )
        if result.returncode != 0:
            logger.warning(f"⚠️  fetch-news.py falló: {result.stderr[:200]}")
            return []

        news = json.loads(result.stdout.strip())
        logger.info(f"   ✅ {len(news)} noticias de fetch-news")
        return news
    except json.JSONDecodeError:
        logger.warning("⚠️  No se pudo parsear output de fetch-news.py")
        return []
    except Exception as e:
        logger.warning(f"⚠️  Error ejecutando fetch-news.py: {e}")
        return []


def scrape_reddit(target_date: str) -> list:
    """Ejecuta fetch-reddit.py y retorna los posts."""
    reddit_script = PROJECT_ROOT / "scripts" / "fetch-reddit.py"
    if not reddit_script.exists():
        return []

    # Solo correr si hay credenciales
    if not os.environ.get("REDDIT_CLIENT_ID"):
        logger.info("   ℹ️  Reddit: sin credenciales, omitiendo")
        return []

    logger.info("📰 Ejecutando fetch-reddit.py...")

    cmd = [
        sys.executable, str(reddit_script),
        "--max-results", "5",
        "--json-only",
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30,
            env=_SUBPROC_ENV, encoding="utf-8",
        )
        if result.returncode != 0:
            return []

        posts = json.loads(result.stdout.strip())
        # Convertir formato reddit a formato news
        news = []
        for post in posts:
            news.append({
                "title": post.get("title", ""),
                "description": post.get("selftext", post.get("description", ""))[:200],
                "url": post.get("url", ""),
                "source": f"Reddit r/{post.get('subreddit', 'unknown')}",
                "published_at": post.get("created_utc", ""),
            })
        logger.info(f"   ✅ {len(news)} posts de Reddit")
        return news
    except Exception as e:
        logger.warning(f"⚠️  Error ejecutando fetch-reddit.py: {e}")
        return []


def deduplicate_news(news_list: list) -> list:
    """Deduplicación por similitud de título."""
    import unicodedata
    import re

    def normalize(text):
        text = text.lower().strip()
        text = unicodedata.normalize("NFKD", text)
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    seen = set()
    unique = []
    for item in news_list:
        key = normalize(item.get("title", ""))
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def _normalize_title(title: str) -> str:
    """Normaliza un título para comparación de dedupe multi-día: minúsculas,
    sin acentos/diacríticos, sin puntuación, espacios colapsados. Reusa el
    mismo criterio de normalización sin acentos que fetch-news._norm, y
    además quita puntuación para que "¡...!" o distinta puntuación entre
    fuentes no impida detectar el duplicado."""
    text = (title or "").lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_recent_titles(reference_date: str, days: int = 3, daily_news_dir: Path = None) -> set:
    """Carga los títulos normalizados de los daily-news de los últimos
    `days` días anteriores a `reference_date` (sin incluir el propio día
    de referencia). Ignora archivos inexistentes o JSON corrupto."""
    news_dir = daily_news_dir if daily_news_dir is not None else DAILY_NEWS_DIR
    ref = datetime.strptime(reference_date, "%Y-%m-%d").date()

    titles = set()
    for offset in range(1, days + 1):
        day = ref - timedelta(days=offset)
        file_path = Path(news_dir) / f"{day.isoformat()}.json"
        if not file_path.exists():
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        for item in data.get("news", []):
            norm_title = _normalize_title(item.get("title", ""))
            if norm_title:
                titles.add(norm_title)

    return titles


def filter_seen_titles(news_list: list, recent_titles: set) -> list:
    """Descarta noticias cuyo título normalizado ya apareció en los
    daily-news recientes (ver load_recent_titles)."""
    if not recent_titles:
        return list(news_list)

    result = []
    for item in news_list:
        norm_title = _normalize_title(item.get("title", ""))
        if norm_title in recent_titles:
            continue
        result.append(item)
    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scraper diario de noticias InforMessi")
    parser.add_argument(
        "--date", default=today_ar(),
        help="Fecha del archivo de noticias (default: hoy)"
    )
    args = parser.parse_args()

    target_date = args.date
    logger.info(f"🚀 InforMessi - Scraper Diario de Noticias")
    logger.info(f"📅 Fecha objetivo: {target_date}")
    logger.info("=" * 50)

    # Recolectar de todas las fuentes
    all_news = []

    news_from_fetch = scrape_news(target_date)
    all_news.extend(news_from_fetch)

    news_from_reddit = scrape_reddit(target_date)
    all_news.extend(news_from_reddit)

    # Deduplicar (dentro del scrape de hoy)
    unique_news = deduplicate_news(all_news)
    logger.info(f"\n📊 Total antes de dedup: {len(all_news)}, después: {len(unique_news)}")

    # Dedupe multi-día: descartar títulos ya vistos en los daily-news de
    # los últimos 3 días (no solo duplicados dentro del propio scrape).
    recent_titles = load_recent_titles(target_date, days=3)
    before_multiday = len(unique_news)
    unique_news = filter_seen_titles(unique_news, recent_titles)
    if before_multiday != len(unique_news):
        logger.info(
            f"   🗑️  Dedupe multi-día: {before_multiday - len(unique_news)} "
            f"noticia(s) descartada(s) por repetirse en días anteriores"
        )

    # Filtro LLM opcional (best-effort, fallback silencioso ante error)
    if os.environ.get("NEWS_LLM_FILTER") == "1":
        before_llm = len(unique_news)
        unique_news = filter_news_llm(unique_news)
        logger.info(f"   🤖 Filtro LLM: {before_llm} -> {len(unique_news)} noticia(s)")

    # Categorizar
    for item in unique_news:
        item["category"] = _categorize_news(item)

    categories = {}
    for item in unique_news:
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1
    logger.info(f"   Categorías: {dict(categories)}")

    # Guardar
    output = {
        "scrape_date": target_date,
        "scraped_at": now_ar_iso(),
        "total_news": len(unique_news),
        "news": unique_news,
    }

    output_file = DAILY_NEWS_DIR / f"{target_date}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"\n✅ Guardado: {output_file}")
    logger.info(f"   {len(unique_news)} noticias")


if __name__ == "__main__":
    main()
