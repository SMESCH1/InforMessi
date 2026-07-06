#!/usr/bin/env python3
"""
Validación de schema de reports de InforMessi.

validate_report(report) -> list[str]
    Lista de errores encontrados (vacía = report válido).

Validación ADITIVA: los campos "siempre obligatorios" son los que ya
existían en reports generados por el pipeline Groq desde el inicio del
proyecto. Los reports con source == "claude-agent" deben cumplir además
un set de requisitos extra (weather, sources, generated_at con offset)
propios del contrato agente-pipeline. Reports viejos sin "source" nunca
deben fallar por los campos nuevos.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from time_utils import parse_ts

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TZ_OFFSET_RE = re.compile(r"(Z|[+-]\d{2}:?\d{2})$")


def _is_valid_date_string(value) -> bool:
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return False
    try:
        from datetime import date

        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _validate_base(report: dict) -> list[str]:
    errors = []

    date_value = report.get("date")
    if not _is_valid_date_string(date_value):
        errors.append(f"'date' inválida o ausente: {date_value!r}")

    generated_at = report.get("generated_at")
    if not generated_at or not isinstance(generated_at, str):
        errors.append(f"'generated_at' ausente o no es string: {generated_at!r}")
    else:
        try:
            parse_ts(generated_at)
        except (ValueError, TypeError) as e:
            errors.append(f"'generated_at' no parseable ({generated_at!r}): {e}")

    data = report.get("data")
    if not isinstance(data, dict):
        errors.append(f"'data' ausente o no es dict: {data!r}")
    else:
        if not isinstance(data.get("events"), list):
            errors.append(f"'data.events' ausente o no es lista: {data.get('events')!r}")
        if not isinstance(data.get("news"), list):
            errors.append(f"'data.news' ausente o no es lista: {data.get('news')!r}")

    message = report.get("message")
    if not isinstance(message, str) or not message.strip():
        errors.append("'message' ausente o vacío")

    status = report.get("status")
    if not isinstance(status, str) or not status:
        errors.append(f"'status' ausente o no es string: {status!r}")

    if "pre_approved" not in report or not isinstance(report.get("pre_approved"), bool):
        errors.append(f"'pre_approved' ausente o no es bool: {report.get('pre_approved')!r}")

    return errors


def _validate_claude_agent(report: dict) -> list[str]:
    errors = []
    data = report.get("data")
    data = data if isinstance(data, dict) else {}

    if "weather" not in data:
        errors.append("source=claude-agent requiere 'data.weather' (dict o null explícito)")
    else:
        weather = data.get("weather")
        if weather is not None and not isinstance(weather, dict):
            errors.append(f"'data.weather' debe ser dict o null: {weather!r}")

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append(f"source=claude-agent requiere 'data.sources' lista no vacía: {sources!r}")
    else:
        bad = [s for s in sources if not (isinstance(s, str) and re.match(r"^https?://", s))]
        if bad:
            errors.append(f"'data.sources' contiene entradas inválidas (deben ser http(s) strings): {bad!r}")

    mundial_start = data.get("mundial_2026_start")
    if not _is_valid_date_string(mundial_start):
        errors.append(
            f"source=claude-agent requiere 'data.mundial_2026_start' con formato YYYY-MM-DD: {mundial_start!r}"
        )

    generated_at = report.get("generated_at")
    if isinstance(generated_at, str) and not _TZ_OFFSET_RE.search(generated_at):
        errors.append(
            f"source=claude-agent requiere 'generated_at' con offset de timezone: {generated_at!r}"
        )

    return errors


def validate_report(report: dict) -> list[str]:
    """Valida un report contra el schema de InforMessi.

    Retorna una lista de mensajes de error (vacía si el report es válido).
    """
    errors = _validate_base(report)

    if report.get("source") == "claude-agent":
        errors.extend(_validate_claude_agent(report))

    return errors


def main():
    import argparse
    import json

    from time_utils import today_ar

    parser = argparse.ArgumentParser(description="Valida el schema de un report de InforMessi")
    parser.add_argument("--date", help="Fecha a validar (YYYY-MM-DD). Default: hoy", default=None)
    args = parser.parse_args()

    target_date = args.date or today_ar()
    report_path = REPORTS_DIR / f"{target_date}.json"

    if not report_path.exists():
        print(f"Report no encontrado: {report_path}")
        sys.exit(1)

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    errors = validate_report(report)

    if errors:
        print(f"Report {target_date} INVÁLIDO ({len(errors)} error(es)):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print(f"Report {target_date} válido.")
    sys.exit(0)


if __name__ == "__main__":
    main()
