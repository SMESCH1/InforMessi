#!/usr/bin/env python3
"""
Script para recolectar todos los datos del día (clima, eventos, noticias)
Fase 4 - InforMessi
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def collect_all_data(date: str = None, include_news: bool = True) -> dict:
    """Recolecta todos los datos del día"""
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    print("📊 Recolectando datos del día...")
    print("=" * 50)
    
    # Clima: Removido (feature futura)
    # El clima se dejó como feature futura, no se incluye en el flujo actual
    
    # Eventos - usar script mejorado
    print("📅 Obteniendo eventos...")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "fetch-events-enhanced.py"), "--date", date],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # Buscar JSON en la salida
            output_lines = result.stdout.strip().split('\n')
            json_line = None
            for line in reversed(output_lines):
                line = line.strip()
                if line.startswith('[') or line.startswith('{'):
                    try:
                        events = json.loads(line)
                        break
                    except:
                        continue
            else:
                events = []
        else:
            events = []
    except Exception as e:
        print(f"⚠️  Error al obtener eventos: {e}, usando solo JSON")
        # Fallback a JSON directo
        events_file = PROJECT_ROOT / "data" / "events.json"
        events = []
        if events_file.exists():
            with open(events_file, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
                date_key = date[5:]  # MM-DD
                events = [
                    e for e in events_data.get("events", [])
                    if isinstance(e.get("date", ""), str) and e.get("date", "")[5:] == date_key
                ]
    
    news = []
    reddit_posts = []
    if include_news:
        # Noticias - usar script de noticias
        print("📰 Obteniendo noticias...")
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
        print("📰 Noticias omitidas (modo --no-news).")
    
    # Combinar noticias y posts de Reddit
    # Convertir posts de Reddit al formato de noticias para consistencia
    reddit_as_news = []
    for post in reddit_posts:
        reddit_as_news.append({
            "title": post.get("title", ""),
            "description": post.get("content", "")[:200],
            "url": post.get("url", ""),
            "source": f"Reddit r/{post.get('subreddit', 'unknown')}",
            "published_at": post.get("created_at", datetime.now().isoformat())
        })
    
    # Combinar todas las noticias
    all_news = news + reddit_as_news
    
    # Calcular días restantes
    mundial_start = "2026-06-11"
    mundial = datetime.strptime(mundial_start, "%Y-%m-%d").date()
    current = datetime.strptime(date, "%Y-%m-%d").date()
    days_remaining = (mundial - current).days
    
    data = {
        "date": date,
        "mundial_2026_start": mundial_start,
        "days_remaining": days_remaining,
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

