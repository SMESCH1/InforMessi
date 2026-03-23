#!/usr/bin/env python3
"""
Genera informes con antelación (15 días por defecto)
MVP - InforMessi
"""

import json
import logging
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Cargar .env si existe (para GROQ_API_KEY, etc.)
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

# UTF-8 en subprocesos (Windows / emojis en prints de otros scripts)
_SUBPROC_ENV = {**os.environ, "PYTHONUTF8": "1"}


def _parse_cli_date(value: str | None, flag: str):
    """Parsea YYYY-MM-DD; evita el error típico: --end-date --overwrite (sin fecha)."""
    if value is None:
        return None
    stripped = value.strip()
    if stripped.startswith("-"):
        logger.error(
            "❌ %s recibió un valor inválido (%r). "
            "¿Falta la fecha? Ejemplo: --end-date 2026-06-10 --overwrite",
            flag,
            stripped,
        )
        sys.exit(2)
    try:
        return datetime.strptime(stripped, "%Y-%m-%d").date()
    except ValueError:
        logger.error(
            "❌ %s debe ser YYYY-MM-DD, recibido: %r",
            flag,
            stripped,
        )
        sys.exit(2)


def generate_report_for_date(
    date: str,
    *,
    include_news: bool = False,
    provider: str = "ollama",
) -> dict:
    """Genera un informe para una fecha específica.

    provider: ollama (LLM local) o groq (API; requiere GROQ_API_KEY en .env).
    """
    logger.info(f"📅 Generando informe para {date}...")

    # Recolectar datos
    data_file = PROJECT_ROOT / "tmp" / f"data-{date}.json"
    data_file.parent.mkdir(exist_ok=True)

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "collect-daily-data.py"),
        "--date",
        date,
        "--output",
        str(data_file),
    ]
    if not include_news:
        cmd.append("--no-news")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            env=_SUBPROC_ENV,
            encoding="utf-8",
        )

        if result.returncode != 0:
            logger.warning(f"⚠️  Error al recolectar datos: {result.stderr}")
            return None

        # Cargar datos
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None

    message_file = PROJECT_ROOT / "tmp" / f"message-{date}.txt"
    gen_env = {**_SUBPROC_ENV, "LLM_PROVIDER": provider}
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "generate-message.py"),
                "--data",
                str(data_file),
                "--output",
                str(message_file),
                "--provider",
                provider,
            ],
            capture_output=True,
            text=True,
            timeout=300,
            env=gen_env,
            encoding="utf-8",
        )
        if result.returncode != 0:
            logger.warning(f"⚠️  Error al generar mensaje: {result.stderr}")
            message = ""
        else:
            message = message_file.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        message = ""

    # Guardar informe
    report = {
        "date": date,
        "generated_at": datetime.now().isoformat(),
        "data": data,
        "message": message,
        "status": "draft",  # draft, updated, published
        "updated_at": None,
        "published_at": None,
        "pre_approved": False,  # Si está pre-aprobado, se publica directamente sin preview
        "pre_approved_at": None,
    }

    report_file = REPORTS_DIR / f"{date}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Informe guardado: {report_file}")
    return report


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Genera informes con antelación",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=15,
        help="Días de antelación a generar (default: 15; ignorado si --end-date)",
    )
    parser.add_argument(
        "--start-date",
        metavar="YYYY-MM-DD",
        help="Fecha de inicio. Default: hoy",
    )
    parser.add_argument(
        "--end-date",
        metavar="YYYY-MM-DD",
        help="Fecha fin inclusive. Si se indica, se generan todas las fechas desde --start-date hasta este día (ignora --days).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerar aunque ya exista el JSON del día",
    )
    parser.add_argument(
        "--with-news",
        action="store_true",
        help="Incluir noticias y Reddit (no pasar --no-news a collect-daily-data)",
    )
    parser.add_argument(
        "--provider",
        choices=["ollama", "groq"],
        default=os.environ.get("LLM_PROVIDER", "ollama"),
        help="Proveedor LLM para generate-message: ollama (local, requiere Ollama) o groq (API, requiere GROQ_API_KEY). Default: env LLM_PROVIDER u ollama.",
    )

    args = parser.parse_args()

    if args.start_date:
        start_d = _parse_cli_date(args.start_date, "--start-date")
    else:
        start_d = datetime.now().date()

    if args.end_date:
        end_d = _parse_cli_date(args.end_date, "--end-date")
        if end_d < start_d:
            logger.error("❌ --end-date no puede ser anterior a la fecha de inicio")
            sys.exit(1)
        dates = []
        cur = start_d
        while cur <= end_d:
            dates.append(cur.isoformat())
            cur += timedelta(days=1)
    else:
        dates = [(start_d + timedelta(days=i)).isoformat() for i in range(args.days)]

    logger.info("🚀 Generando informes con antelación")
    logger.info("=" * 50)
    logger.info(f"📅 Fecha inicio: {start_d.isoformat()}")
    logger.info(f"📅 Fechas a procesar: {len(dates)}")
    logger.info(f"📰 Con noticias: {args.with_news}")
    logger.info(f"🤖 Proveedor LLM: {args.provider}")
    logger.info(f"♻️  Sobrescribir existentes: {args.overwrite}")
    logger.info("")

    generated = 0
    failed = 0
    skipped = 0

    for date_str in dates:
        report_file = REPORTS_DIR / f"{date_str}.json"
        if report_file.exists() and not args.overwrite:
            logger.info(f"⏭️  Informe para {date_str} ya existe, omitiendo...")
            skipped += 1
            continue

        report = generate_report_for_date(
            date_str,
            include_news=args.with_news,
            provider=args.provider,
        )
        if report:
            generated += 1
        else:
            failed += 1
        logger.info("")

    logger.info("=" * 50)
    logger.info(f"✅ Informes generados: {generated}")
    if skipped:
        logger.info(f"⏭️  Omitidos (ya existían): {skipped}")
    if failed > 0:
        logger.error(f"❌ Informes fallidos: {failed}")
    logger.info(f"📁 Ubicación: {REPORTS_DIR}")


if __name__ == "__main__":
    main()
