#!/usr/bin/env python3
"""
Utilidades de timezone para InforMessi.

Todo el pipeline debe operar en hora Argentina (America/Argentina/Buenos_Aires,
UTC-3), independientemente de que corra en GitHub Actions (ubuntu-latest, UTC)
o en una máquina local. Usar SIEMPRE estas funciones en lugar de
`datetime.now()` / `datetime.utcnow()` para obtener la fecha/hora "actual".

No usar `time.tzset()` ni `os.environ['TZ']`: no funcionan en Windows.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

TZ_AR = ZoneInfo("America/Argentina/Buenos_Aires")


def now_ar() -> datetime:
    """Fecha/hora actual, aware, en timezone Argentina."""
    return datetime.now(tz=TZ_AR)


def today_ar() -> str:
    """Fecha actual en Argentina, formato YYYY-MM-DD."""
    return now_ar().strftime("%Y-%m-%d")


def now_ar_iso() -> str:
    """Fecha/hora actual en Argentina, isoformat con offset (-03:00)."""
    return now_ar().isoformat()


def parse_ts(s: str) -> datetime:
    """
    Parsea un timestamp ISO. Si el resultado es naive (sin tzinfo),
    asume timezone Argentina — necesario para compatibilidad con reports
    viejos que tienen timestamps naive (generados antes de este fix).
    """
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ_AR)
    return dt


def hours_since(ts: str) -> float:
    """Horas transcurridas desde el timestamp `ts` (string ISO) hasta ahora."""
    return (now_ar() - parse_ts(ts)).total_seconds() / 3600
