#!/usr/bin/env python3
"""
Genera informes con antelación (15 días por defecto)
MVP - InforMessi
"""

import json
import logging
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def generate_report_for_date(date: str) -> dict:
    """Genera un informe para una fecha específica"""
    logger.info(f"📅 Generando informe para {date}...")
    
    # Recolectar datos
    data_file = PROJECT_ROOT / "tmp" / f"data-{date}.json"
    data_file.parent.mkdir(exist_ok=True)
    
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "collect-daily-data.py"),
             "--date", date, "--output", str(data_file), "--no-news"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            logger.warning(f"⚠️  Error al recolectar datos: {result.stderr}")
            return None
            
        # Cargar datos
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None
    
    has_events = bool(data.get("events"))
    has_news = bool(data.get("news"))

    if not has_events and not has_news:
        logger.info(f"ℹ️  Sin eventos ni noticias para {date}, guardando borrador sin mensaje")
        message = ""
    else:
        message_file = PROJECT_ROOT / "tmp" / f"message-{date}.txt"
        try:
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "scripts" / "generate-message.py"),
                 "--data", str(data_file), "--output", str(message_file)],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                logger.warning(f"⚠️  Error al generar mensaje: {result.stderr}")
                message = ""
            else:
                message = message_file.read_text(encoding='utf-8')
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
        "pre_approved_at": None
    }
    
    report_file = REPORTS_DIR / f"{date}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Informe guardado: {report_file}")
    return report


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Genera informes con antelación"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=15,
        help="Días de antelación a generar (default: 15)"
    )
    parser.add_argument(
        "--start-date",
        help="Fecha de inicio (YYYY-MM-DD). Default: hoy"
    )
    
    args = parser.parse_args()
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    else:
        start_date = datetime.now()
    
    logger.info("🚀 Generando informes con antelación")
    logger.info("=" * 50)
    logger.info(f"📅 Fecha inicio: {start_date.strftime('%Y-%m-%d')}")
    logger.info(f"📊 Días a generar: {args.days}")
    logger.info("")
    
    generated = 0
    failed = 0
    
    for i in range(args.days):
        target_date = start_date + timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        
        # Verificar si ya existe
        report_file = REPORTS_DIR / f"{date_str}.json"
        if report_file.exists():
            logger.info(f"⏭️  Informe para {date_str} ya existe, omitiendo...")
            continue
        
        report = generate_report_for_date(date_str)
        if report:
            generated += 1
        else:
            failed += 1
        logger.info("")
    
    logger.info("=" * 50)
    logger.info(f"✅ Informes generados: {generated}")
    if failed > 0:
        logger.error(f"❌ Informes fallidos: {failed}")
    logger.info(f"📁 Ubicación: {REPORTS_DIR}")


if __name__ == "__main__":
    main()

