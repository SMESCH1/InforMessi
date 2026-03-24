#!/usr/bin/env python3
"""
Script para recolectar todos los datos del día (eventos, noticias)
Fase 4 - InforMessi
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Evita UnicodeEncodeError en consolas Windows (cp1252) al imprimir emojis
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _load_scraped_news(date: str) -> list:
    """Lee noticias pre-scrapeadas desde data/daily-news/ si existen."""
    from datetime import timedelta

    daily_news_dir = PROJECT_ROOT / "data" / "daily-news"

    # Intentar fecha de hoy, luego ayer
    for offset in (0, 1):
        d = datetime.strptime(date, "%Y-%m-%d").date() - timedelta(days=offset)
        f = daily_news_dir / f"{d.isoformat()}.json"
        if f.exists():
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                news = data.get("news", [])
                if news:
                    print(f"📰 Noticias scrapeadas encontradas: {f.name} ({len(news)} items)")
                    return news
            except Exception as e:
                print(f"⚠️  Error al leer {f.name}: {e}")
    return []


def collect_all_data(date: str = None, include_news: bool = True) -> dict:
    """Recolecta todos los datos del día"""

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    print("📊 Recolectando datos del día...")
    print("=" * 50)
    
    # Clima: Removido (feature futura)
    # El clima se dejó como feature futura, no se incluye en el flujo actual
    
    # Eventos - usar script mejorado, con fallback directo a events.json
    print("📅 Obteniendo eventos...")
    events = []
    try:
        _env = {**os.environ, "PYTHONUTF8": "1"}
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "fetch-events-enhanced.py"), "--date", date],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            env=_env
        )
        if result.returncode == 0:
            # Buscar JSON en la salida (single-line o multi-line)
            output_lines = result.stdout.strip().split('\n')
            # Primero intentar línea por línea (JSON single-line)
            for line in reversed(output_lines):
                line = line.strip()
                if line.startswith('[') or line.startswith('{'):
                    try:
                        events = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue
            # Si no encontró, intentar parsear toda la salida buscando el JSON completo
            if not events:
                full_output = result.stdout.strip()
                # Buscar el último bloque JSON válido en la salida
                bracket_start = full_output.rfind('\n[')
                if bracket_start >= 0:
                    try:
                        events = json.loads(full_output[bracket_start + 1:])
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        print(f"⚠️  Error al ejecutar fetch-events-enhanced.py: {e}")

    # Fallback: leer events.json directamente si no se obtuvieron eventos
    if not events:
        print("📅 Fallback: leyendo eventos directamente desde events.json...")
        events_file = PROJECT_ROOT / "data" / "events.json"
        if events_file.exists():
            try:
                with open(events_file, 'r', encoding='utf-8') as f:
                    events_data = json.load(f)
                date_key = date[5:]  # MM-DD
                target_year = int(date[:4])
                for e in events_data.get("events", []):
                    event_date = e.get("date", "")
                    if isinstance(event_date, str) and len(event_date) >= 10 and event_date[5:] == date_key:
                        ev = dict(e)
                        # Recalcular edad para birthdays
                        if ev.get("type") == "birthday" and "age" in ev:
                            birth_year = int(event_date[:4])
                            ev["age"] = target_year - birth_year
                            ev["description"] = f"Cumpleaños de {ev.get('person', '')} ({ev['age']} años)"
                        events.append(ev)
                # Ordenar por prioridad
                priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
                events.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
            except Exception as e:
                print(f"⚠️  Error al leer events.json: {e}")
    
    news = []
    reddit_posts = []
    if include_news:
        # Primero: intentar leer noticias scrapeadas (del workflow nocturno)
        scraped_news = _load_scraped_news(date)

        # Luego: fetch live como suplemento
        print("📰 Obteniendo noticias frescas...")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "fetch-news.py"),
                    "--max-results", "3",
                    "--json-only",
                    "--date", date
                ],
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

        # Reddit - obtener posts relevantes
        print("🔴 Obteniendo posts de Reddit...")
        try:
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "scripts" / "fetch-reddit.py"), "--max-results", "3", "--json-only"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                # Buscar JSON en la salida (puede haber mensajes antes)
                json_found = False
                for line in output.split('\n'):
                    line = line.strip()
                    if line.startswith('['):
                        try:
                            reddit_posts = json.loads(line)
                            json_found = True
                            break
                        except json.JSONDecodeError:
                            continue
                if not json_found:
                    # Intentar parsear toda la salida como JSON
                    try:
                        reddit_posts = json.loads(output)
                    except:
                        reddit_posts = []
            else:
                print(f"⚠️  Error en fetch-reddit.py: {result.stderr}")
                reddit_posts = []
        except Exception as e:
            print(f"⚠️  Error al obtener posts de Reddit: {e}")
            reddit_posts = []
    else:
        scraped_news = []
        print("📰 Noticias omitidas (modo --no-news).")
    
    # Combinar noticias y posts de Reddit
    reddit_as_news = []
    for post in reddit_posts:
        reddit_as_news.append({
            "title": post.get("title", ""),
            "description": post.get("content", "")[:200],
            "url": post.get("url", ""),
            "source": f"Reddit r/{post.get('subreddit', 'unknown')}",
            "published_at": post.get("created_at", datetime.now().isoformat())
        })

    # Combinar: scrapeadas (prioridad) + live + reddit
    all_news = scraped_news + news + reddit_as_news

    # Filtrar noticias usadas recientemente (últimos 7 días) para evitar repetición
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from rag_memory_database import MemoryDatabase
        import unicodedata
        db = MemoryDatabase()
        used_news = db.data.get("news_topics", {})
        def _norm(t):
            t = t.lower().strip()
            t = unicodedata.normalize("NFD", t)
            t = "".join(c for c in t if unicodedata.category(c) != "Mn")
            return " ".join(t.split())[:50]
        recent_used = set()
        from datetime import timedelta
        cutoff = datetime.strptime(date, "%Y-%m-%d").date() - timedelta(days=7)
        for norm_title, dates_used in used_news.items():
            for d in dates_used:
                try:
                    if datetime.strptime(d, "%Y-%m-%d").date() >= cutoff:
                        recent_used.add(norm_title)
                        break
                except Exception:
                    continue
        filtered_news = []
        for item in all_news:
            title_norm = _norm(item.get("title", ""))
            if title_norm not in recent_used:
                filtered_news.append(item)
            else:
                print(f"   🚫 Noticia filtrada (ya usada recientemente): {item.get('title', '')[:60]}")
        all_news = filtered_news
    except Exception as e:
        print(f"⚠️  No se pudo filtrar noticias repetidas: {e}")

    # Calcular días restantes y fase del Mundial
    mundial_start = "2026-06-11"
    mundial_end = "2026-07-19"
    mundial = datetime.strptime(mundial_start, "%Y-%m-%d").date()
    mundial_fin = datetime.strptime(mundial_end, "%Y-%m-%d").date()
    current = datetime.strptime(date, "%Y-%m-%d").date()
    days_remaining = (mundial - current).days

    if current < mundial:
        mundial_phase = "pre_mundial"
        mundial_day = None
    elif current <= mundial_fin:
        mundial_phase = "durante_mundial"
        mundial_day = (current - mundial).days + 1
    else:
        mundial_phase = "post_mundial"
        mundial_day = None

    data = {
        "date": date,
        "mundial_2026_start": mundial_start,
        "mundial_2026_end": mundial_end,
        "days_remaining": days_remaining,
        "mundial_phase": mundial_phase,
        "mundial_day": mundial_day,
        "events": events,
        "news": all_news
    }
    
    print()
    print("✅ Datos recolectados:")
    print(f"   Fecha: {date}")
    print(f"   Días restantes: {days_remaining}")
    print(f"   Eventos: {len(events)}")
    print(f"   Noticias: {len(news)}")
    print(f"   Reddit: {len(reddit_posts)}")
    print(f"   Total noticias: {len(all_news)}")
    
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
    parser.add_argument(
        "--no-news",
        action="store_true",
        help="No incluir noticias ni Reddit (útil para generación anticipada)"
    )
    
    args = parser.parse_args()
    
    data = collect_all_data(args.date, include_news=not args.no_news)
    
    # Guardar
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Datos guardados en: {args.output}")


if __name__ == "__main__":
    main()

