#!/usr/bin/env python3
"""
Actualiza el informe del día con las últimas noticias y eventos
MVP - InforMessi
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from time_utils import now_ar_iso, today_ar

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass


def _llm_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "ollama")


def update_report_for_date(date: str) -> bool:
    """Actualiza el informe de una fecha específica"""
    report_file = REPORTS_DIR / f"{date}.json"
    
    if not report_file.exists():
        logger.warning(f"⚠️  Informe para {date} no existe. Generando nuevo informe...")
        # Generar nuevo informe
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "generate-advance-reports.py"),
                "--days",
                "1",
                "--start-date",
                date,
                "--provider",
                _llm_provider(),
            ],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    
    logger.info(f"📅 Actualizando informe para {date}...")
    
    # Cargar informe existente
    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Recolectar datos actualizados
    data_file = PROJECT_ROOT / "tmp" / f"data-{date}.json"
    data_file.parent.mkdir(exist_ok=True)
    
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "collect-daily-data.py"),
             "--date", date, "--output", str(data_file)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            logger.warning(f"⚠️  Error al recolectar datos: {result.stderr}")
            return False
            
        # Cargar datos actualizados
        with open(data_file, 'r', encoding='utf-8') as f:
            updated_data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False
    
    def _normalize_news_titles(items):
        return sorted([item.get("title", "").strip() for item in items if item.get("title")])

    def _normalize_event_desc(items):
        return sorted([item.get("description", "").strip() for item in items if item.get("description")])

    old_news_titles = _normalize_news_titles(report.get("data", {}).get("news", []))
    new_news_titles = _normalize_news_titles(updated_data.get("news", []))

    old_event_desc = _normalize_event_desc(report.get("data", {}).get("events", []))
    new_event_desc = _normalize_event_desc(updated_data.get("events", []))

    has_changes = (old_news_titles != new_news_titles) or (old_event_desc != new_event_desc)
    
    if not has_changes:
        logger.info("ℹ️  No hay cambios significativos en los datos")
        return True
    
    logger.info(f"📊 Cambios detectados:")
    logger.info(f"   Noticias: {len(old_news_titles)} → {len(new_news_titles)}")
    logger.info(f"   Eventos: {len(old_event_desc)} → {len(new_event_desc)}")
    
    # Regenerar mensaje con datos actualizados
    message_file = PROJECT_ROOT / "tmp" / f"message-{date}.txt"
    
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
                _llm_provider(),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        if result.returncode != 0:
            logger.warning(f"⚠️  Error al generar mensaje: {result.stderr}")
            return False
            
        # Leer mensaje actualizado
        updated_message = message_file.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False
    
    # Actualizar informe
    report["data"] = updated_data
    report["message"] = updated_message
    report["status"] = "updated"
    report["updated_at"] = now_ar_iso()
    report["pre_approved"] = True
    report["pre_approved_at"] = now_ar_iso()
    
    # Guardar
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # La memoria se actualiza solo al publicar (send-daily, auto-publish, webhook, publish-approved)
    logger.info(f"✅ Informe actualizado: {report_file}")
    return True


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Actualiza el informe del día con datos actualizados"
    )
    parser.add_argument(
        "--date",
        help="Fecha a actualizar (YYYY-MM-DD). Default: hoy"
    )
    
    args = parser.parse_args()
    
    if args.date:
        target_date = args.date
    else:
        target_date = today_ar()
    
    logger.info("🔄 Actualizando informe del día")
    logger.info("=" * 50)
    logger.info(f"📅 Fecha: {target_date}")
    logger.info("")
    
    success = update_report_for_date(target_date)
    
    if success:
        logger.info("")
        logger.info("=" * 50)
        logger.info("✅ Actualización completada")
    else:
        logger.info("")
        logger.info("=" * 50)
        logger.error("❌ Error en la actualización")
        sys.exit(1)


if __name__ == "__main__":
    main()

