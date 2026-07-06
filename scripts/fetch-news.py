#!/usr/bin/env python3
"""
Script para obtener noticias deportivas de Argentina y fútbol mundial
Fase 4 - InforMessi
"""

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parent))
from time_utils import now_ar, now_ar_iso, today_ar
from text_utils import normalize_text as _norm
from llm_client import call_groq, LLMClientError

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

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

# Keywords fuertes: si aparecen, la noticia es futbolística/Selección con
# confianza alta. Se usan tanto para exigir relevancia mínima como para
# "salvar" noticias de la blacklist (ver has_strong_football_signal).
KEYWORDS_STRONG = [
    "seleccion", "messi", "scaloni", "scaloneta", "mundial", "afa", "fifa",
    "albiceleste", "copa america", "eliminatorias", "conmebol",
]

# Subconjunto de KEYWORDS_STRONG que son nombres propios o apodos (jugador,
# DT, apodos del equipo) en vez de términos futbolísticos genéricos. Un
# nombre propio (solo o combinado con otros nombres propios) puede aparecer
# en una nota de farándula/policiales sin que la nota sea sobre fútbol — por
# eso NO alcanza por sí solo para anular un match de blacklist (ver
# _has_non_proper_strong_signal). Los nombres de jugadores cargados desde
# data/players.json también se consideran nombres propios.
KEYWORDS_STRONG_PROPER_NOUNS = {
    "messi", "scaloni", "scaloneta", "afa", "albiceleste",
}

# Términos futbolísticos genéricos: solos no alcanzan, pero combinados con
# "argentina" sí indican contexto futbolístico fuerte. OJO: muchos de estos
# son ambiguos fuera de contexto futbolístico ("entrenador" personal de
# gimnasio, "jugador" de poker, "partido" de truco/cartas/política) — por
# eso este set se usa para relevancia general (junto con "argentina"), pero
# NO alcanza para anular la blacklist (ver FOOTBALL_UNAMBIGUOUS_TERMS y
# _has_non_proper_strong_signal).
FOOTBALL_CONTEXT_TERMS = [
    "partido", "gol", "goles", "estadio", "tecnico", "convocatoria",
    "lesion", "futbol", "football", "liga", "torneo", "arquero",
    "delantero", "defensor", "mediocampista", "entrenador", "cancha",
    "jugador", "jugadores", "plantel", "amistoso", "clasico",
]

# Términos futbolísticos INEQUÍVOCOS: la palabra sola ya implica fútbol/
# Selección Argentina, sin ambigüedad razonable en otro dominio (a
# diferencia de "entrenador", "jugador", "partido", "gol", "técnico", que
# son términos de FOOTBALL_CONTEXT_TERMS pero se usan en muchos otros
# contextos: entrenador personal, jugador de poker, partido de truco/
# política, gol de una campaña de marketing, técnico de PC, etc.). Se usa
# exclusivamente para la regla anti-blacklist: para anular un match de
# blacklist hace falta 2+ señales fuertes Y al menos una de este set.
#
# Nota: "afa" y "scaloneta" quedan afuera a propósito aunque sean
# inequívocamente futbolísticos, porque están clasificados como nombres
# propios/apodos en KEYWORDS_STRONG_PROPER_NOUNS (una nota de farándula
# puede nombrar "la Scaloneta" o "la AFA" de pasada sin ser sobre fútbol,
# igual que puede nombrar a "Messi" o "Scaloni") — deben poder repetirse
# junto a otros nombres propios sin anular la blacklist por sí solos (ver
# test_farandula_milei_scaloni_almuerzo_rechazada).
FOOTBALL_UNAMBIGUOUS_TERMS = [
    "mundial", "fifa", "seleccion argentina", "seleccion", "eliminatorias",
    "conmebol", "copa america", "convocatoria",
    "amistoso", "hinchada", "estadio",
]

# Noticias basura frecuentes que pasan el filtro laxo actual: política,
# farándula/policiales, apuestas, negocios no futbolísticos, autos/lujo.
KEYWORDS_BLACKLIST = [
    # política
    "elecciones", "milei", "congreso", "gobierno", "senado", "diputados",
    "candidato", "campaña electoral", "ministro", "ministerio",
    # apuestas
    "quiniela", "cuotas", "apuestas", "casa de apuestas", "bono de bienvenida",
    # negocios no futbolísticos
    "telecom", "operador", "acciones", "bolsa", "cotización", "dólar blue",
    "criptomoneda", "inflación",
    # autos/lujo/farándula
    "coche", "auto de lujo", "mansión", "ferrari", "lamborghini",
    "farándula", "escándalo", "polémica amorosa", "chimento",
]

_PLAYER_NAMES_CACHE: Optional[List[str]] = None


def _load_player_names() -> List[str]:
    """Carga nombres de jugadores desde data/players.json (normalizados),
    si el archivo existe. Devuelve lista vacía ante cualquier error."""
    global _PLAYER_NAMES_CACHE
    if _PLAYER_NAMES_CACHE is not None:
        return _PLAYER_NAMES_CACHE

    names = []
    try:
        players_path = Path(__file__).parent.parent / "data" / "players.json"
        with open(players_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for player in data.get("players", []):
            full_name = player.get("name", "")
            if not full_name:
                continue
            # Nombres pueden venir con apodos entre comillas, ej: Emiliano 'Dibu' Martínez
            clean_name = re.sub(r"['\"][^'\"]*['\"]", "", full_name)
            for part in clean_name.split():
                norm_part = _norm(part)
                if len(norm_part) > 3:  # evitar matchear partículas cortas
                    names.append(norm_part)
    except Exception:
        names = []

    _PLAYER_NAMES_CACHE = names
    return names


def _count_strong_signals(norm_text: str) -> int:
    """Cuenta cuántos keywords fuertes distintos (KEYWORDS_STRONG o nombres
    de jugadores) aparecen en el texto normalizado. Un solo match (ej. la
    palabra "mundial" suelta) puede ser incidental (el Mundial de otra
    cosa); varios matches distintos son una señal mucho más confiable de
    que la nota es realmente sobre Selección/fútbol."""
    count = sum(1 for kw in KEYWORDS_STRONG if kw in norm_text)
    count += sum(1 for player_name in _load_player_names() if player_name in norm_text)
    return count


def _has_non_proper_strong_signal(norm_text: str) -> bool:
    """True si el texto tiene al menos una señal fuerte que NO sea un
    nombre propio/apodo (jugador, DT, apodo del equipo) Y que sea
    INEQUÍVOCAMENTE futbolística. Nombres de jugadores conocidos convocados
    (players.json) y los apodos/nombres propios de
    KEYWORDS_STRONG_PROPER_NOUNS no cuentan: una nota de farándula puede
    mencionar a Messi, Scaloni o varios jugadores sin ser una noticia
    futbolística (ej. "el escándalo amoroso entre Messi y Rulli").

    Importante: términos de FOOTBALL_CONTEXT_TERMS como "entrenador",
    "jugador" o "partido" tampoco alcanzan acá, porque son ambiguos fuera
    de contexto futbolístico (entrenador personal de gimnasio, jugador de
    poker, partido de truco/política) y una nota de farándula/policiales
    puede usarlos en ese sentido no futbolístico. Solo cuentan los
    términos de FOOTBALL_UNAMBIGUOUS_TERMS (mundial, fifa, selección,
    eliminatorias, conmebol, copa américa, afa, scaloneta, convocatoria,
    amistoso, hinchada, estadio), donde la palabra sola ya implica fútbol
    sin ambigüedad razonable."""
    non_proper_strong = [
        kw for kw in KEYWORDS_STRONG if kw not in KEYWORDS_STRONG_PROPER_NOUNS
    ]
    if any(kw in norm_text for kw in non_proper_strong):
        return True
    if any(term in norm_text for term in FOOTBALL_UNAMBIGUOUS_TERMS):
        return True
    return False


def has_strong_football_signal(text: str) -> bool:
    """True si el texto tiene una señal futbolística/Selección fuerte:
    keyword fuerte, nombre de jugador convocado, o "argentina" combinado
    con un término futbolístico genérico."""
    norm_text = _norm(text)

    if _count_strong_signals(norm_text) >= 1:
        return True

    if "argentina" in norm_text and any(term in norm_text for term in FOOTBALL_CONTEXT_TERMS):
        return True

    return False


def _matches_blacklist(text: str) -> bool:
    norm_text = _norm(text)
    return any(_norm(kw) in norm_text for kw in KEYWORDS_BLACKLIST)


def filter_news_llm(news_list: List[Dict]) -> List[Dict]:
    """Filtra noticias con una única llamada al LLM (Groq), pidiéndole que
    devuelva los índices de las noticias relevantes (fútbol/Mundial
    2026/Selección Argentina), excluyendo política/farándula/negocios/otros
    deportes.

    Best-effort: ante CUALQUIER error (sin GROQ_API_KEY, error de red, JSON
    inválido, etc.) se retorna la lista original sin filtrar — el filtro
    por keywords ya aplicado en _validate_news_basic sigue siendo la red de
    seguridad principal. Nunca debe hacer fallar el pipeline del scraper.
    """
    if not news_list:
        return news_list

    titles = "\n".join(f"{i}. {n.get('title', '')}" for i, n in enumerate(news_list))
    prompt = (
        "Estas son noticias numeradas. Devolvé SOLO un JSON con la forma "
        '{"relevantes": [indices]} de las noticias que sean sobre fútbol, '
        "el Mundial 2026 o la Selección Argentina, excluyendo política, "
        "farándula, negocios no futbolísticos u otros deportes.\n\n"
        f"{titles}"
    )

    try:
        response = call_groq(
            prompt,
            model="llama-3.1-8b-instant",
            json_mode=True,
            temperature=0,
        )
        data = json.loads(response)
        indices = data["relevantes"]
        filtered = [
            news_list[i] for i in indices
            if isinstance(i, int) and 0 <= i < len(news_list)
        ]
        return filtered
    except LLMClientError as e:
        # Caso esperado (ej. GROQ_API_KEY no configurada en local/dev): no es
        # un error real, solo degradación best-effort. No amerita warning.
        logger.info(f"ℹ️  filter_news_llm: sin filtro LLM disponible ({e})")
        return news_list
    except Exception as e:
        # Error real de red, parsing de JSON, índices inesperados, etc. —
        # sí es una condición anómala que conviene ver como warning.
        logger.warning(f"⚠️  filter_news_llm: fallback silencioso ({e})")
        return news_list


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
            today = now_ar().date()
    else:
        today = now_ar().date()

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

        # Primero: exigir relevancia futbolística mínima (señal fuerte o
        # "argentina" + término de contexto). Sin esto no alcanza el umbral
        # mínimo, matchee o no la blacklist.
        if not has_strong_football_signal(text):
            continue

        # Orden de evaluación: la señal futbolística fuerte gana sobre la
        # blacklist, pero no con un solo match incidental, y no solo con
        # nombres propios. Ej. "Digi ha perdido el tren del Mundial"
        # (telecom) tiene una única palabra fuerte ("mundial") que aparece
        # de pura casualidad — no alcanza. "El escándalo amoroso entre
        # Messi y Rulli sacude la farándula" tiene DOS señales fuertes
        # (dos nombres de jugadores) pero CERO no-nombre-propio — no
        # alcanza: los nombres propios solos no acreditan que la nota sea
        # futbolística, ya que farándula/policiales frecuentemente
        # mencionan jugadores. En cambio "El gobierno de la FIFA definió
        # el nuevo formato de eliminatorias... Mundial 2026" tiene varias
        # señales fuertes distintas ("fifa", "eliminatorias", "mundial"),
        # todas no-nombre-propio: ahí sí gana sobre la blacklist
        # ("gobierno"). Se requieren 2+ señales fuertes distintas Y AL
        # MENOS UNA no-nombre-propio para "salvar" una noticia que matchea
        # la blacklist.
        if _matches_blacklist(text) and (
            _count_strong_signals(_norm(text)) < 2
            or not _has_non_proper_strong_signal(_norm(text))
        ):
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
                                "published_at": now_ar_iso()
                            })

                if news:
                    break

            except Exception:
                continue

        return news[:max_results]
    except Exception:
        return []


def get_news_argentina(max_results: int = 8, silent: bool = False, reference_date: Optional[str] = None, max_days: int = 3, broad: bool = False, llm_filter: bool = False) -> List[Dict]:
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

    # Filtro LLM opcional (best-effort, fallback silencioso ante error)
    if llm_filter or os.getenv("NEWS_LLM_FILTER") == "1":
        validated_news = filter_news_llm(validated_news)

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
    parser.add_argument(
        "--llm-filter", action="store_true",
        help="Aplicar filtro adicional por LLM (Groq). También se activa con NEWS_LLM_FILTER=1"
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
        llm_filter=args.llm_filter,
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
            output_data = {"date": today_ar(), "news": news}
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Datos guardados en: {args.output}")

        print(json.dumps(news, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
