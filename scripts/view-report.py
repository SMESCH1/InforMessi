#!/usr/bin/env python3
"""
Visualiza un informe de forma legible y amigable
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"


def view_report(date: str):
    """Muestra un informe de forma legible"""
    report_file = REPORTS_DIR / f"{date}.json"
    
    if not report_file.exists():
        print(f"❌ Informe para {date} no encontrado")
        print(f"   Ubicación: {report_file}")
        sys.exit(1)
    
    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Mostrar información
    print("=" * 70)
    print(f"📅 INFORME - {date}")
    print("=" * 70)
    print()
    
    # Estado
    status = report.get("status", "draft")
    status_emoji = {
        "draft": "📝",
        "updated": "✏️",
        "published": "✅"
    }.get(status, "❓")
    
    print(f"{status_emoji} Estado: {status.upper()}")
    print(f"📅 Generado: {report.get('generated_at', 'N/A')}")
    if report.get("updated_at"):
        print(f"✏️  Actualizado: {report.get('updated_at')}")
    if report.get("published_at"):
        print(f"📤 Publicado: {report.get('published_at')}")
    print()
    
    # Datos del día
    data = report.get("data", {})
    print("📊 DATOS DEL DÍA")
    print("-" * 70)
    print(f"   Días restantes al Mundial: {data.get('days_remaining', 'N/A')}")
    print(f"   Eventos: {len(data.get('events', []))}")
    print(f"   Noticias: {len(data.get('news', []))}")
    print()
    
    # Eventos
    events = data.get("events", [])
    if events:
        print("📅 EVENTOS")
        print("-" * 70)
        for event in events[:5]:  # Mostrar máximo 5
            event_type = event.get("type", "unknown")
            desc = event.get("description", "Sin descripción")
            priority = event.get("priority", "low")
            print(f"   [{priority.upper()}] {event_type}: {desc[:60]}...")
        if len(events) > 5:
            print(f"   ... y {len(events) - 5} evento(s) más")
        print()
    
    # Noticias
    news = data.get("news", [])
    if news:
        print("📰 NOTICIAS")
        print("-" * 70)
        for item in news[:3]:  # Mostrar máximo 3
            title = item.get("title", "Sin título")
            source = item.get("source", "Sin fuente")
            print(f"   • {title[:50]}... ({source})")
        if len(news) > 3:
            print(f"   ... y {len(news) - 3} noticia(s) más")
        print()
    
    # Mensaje
    message = report.get("message", "")
    print("📝 MENSAJE")
    print("-" * 70)
    print(message)
    print()
    print("=" * 70)
    
    # Estadísticas
    word_count = len(message.split())
    print(f"📊 Palabras: {word_count} (objetivo: 90-130)")
    print("=" * 70)


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Visualiza un informe de forma legible"
    )
    parser.add_argument(
        "--date",
        help="Fecha a visualizar (YYYY-MM-DD). Default: hoy"
    )
    
    args = parser.parse_args()
    
    if args.date:
        target_date = args.date
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    view_report(target_date)


if __name__ == "__main__":
    main()

