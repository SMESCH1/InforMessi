#!/usr/bin/env python3
"""
Estadísticas de cobertura de reports para InforMessi.
Muestra: total reports, % con eventos, % con mensaje, por status, fechas faltantes.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

# Evita UnicodeEncodeError en consolas Windows
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Estadisticas de cobertura de reports InforMessi")
    parser.add_argument("--start", default="2026-03-15", help="Fecha inicio (YYYY-MM-DD)")
    parser.add_argument("--end", default="2026-07-19", help="Fecha fin (YYYY-MM-DD)")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()

    total_days = (end - start).days + 1

    # Scan all reports
    stats = {
        "total_reports": 0,
        "with_events": 0,
        "with_news": 0,
        "with_message": 0,
        "by_status": {},
        "missing_dates": [],
        "empty_message_dates": [],
    }

    for day_offset in range(total_days):
        date = start + timedelta(days=day_offset)
        date_str = date.isoformat()
        report_file = REPORTS_DIR / f"{date_str}.json"

        if not report_file.exists():
            stats["missing_dates"].append(date_str)
            continue

        stats["total_reports"] += 1

        try:
            with open(report_file, "r", encoding="utf-8") as f:
                report = json.load(f)
        except Exception:
            continue

        data = report.get("data", {})
        events = data.get("events", [])
        news = data.get("news", [])
        message = report.get("message", "")
        status = report.get("status", "unknown")

        if events:
            stats["with_events"] += 1
        if news:
            stats["with_news"] += 1
        if message and len(message.strip()) > 20:
            stats["with_message"] += 1
        else:
            stats["empty_message_dates"].append(date_str)

        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

    # Print report
    print("=" * 60)
    print("  InforMessi - Estadisticas de Cobertura")
    print("=" * 60)
    print(f"  Periodo: {args.start} a {args.end} ({total_days} dias)")
    print(f"  Reports existentes: {stats['total_reports']}/{total_days} ({stats['total_reports']*100//total_days}%)")
    print(f"  Con eventos: {stats['with_events']}/{stats['total_reports']} ({stats['with_events']*100//(stats['total_reports'] or 1)}%)")
    print(f"  Con noticias: {stats['with_news']}/{stats['total_reports']} ({stats['with_news']*100//(stats['total_reports'] or 1)}%)")
    print(f"  Con mensaje: {stats['with_message']}/{stats['total_reports']} ({stats['with_message']*100//(stats['total_reports'] or 1)}%)")
    print()

    print("  Por status:")
    for status, count in sorted(stats["by_status"].items()):
        print(f"    {status}: {count}")
    print()

    if stats["missing_dates"]:
        print(f"  Fechas sin report ({len(stats['missing_dates'])}):")
        for d in stats["missing_dates"][:10]:
            print(f"    - {d}")
        if len(stats["missing_dates"]) > 10:
            print(f"    ... y {len(stats['missing_dates']) - 10} mas")
    else:
        print("  Todas las fechas tienen report!")

    if stats["empty_message_dates"]:
        print(f"\n  Fechas sin mensaje ({len(stats['empty_message_dates'])}):")
        for d in stats["empty_message_dates"][:10]:
            print(f"    - {d}")
        if len(stats["empty_message_dates"]) > 10:
            print(f"    ... y {len(stats['empty_message_dates']) - 10} mas")

    print("=" * 60)


if __name__ == "__main__":
    main()
