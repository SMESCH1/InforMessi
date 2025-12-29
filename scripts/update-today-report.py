#!/usr/bin/env python3
"""
Actualiza el informe del día con las últimas noticias y eventos
MVP - InforMessi
"""

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"


def update_report_for_date(date: str) -> bool:
    """Actualiza el informe de una fecha específica"""
    report_file = REPORTS_DIR / f"{date}.json"
    
    if not report_file.exists():
        print(f"⚠️  Informe para {date} no existe. Generando nuevo informe...")
        # Generar nuevo informe
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "generate-advance-reports.py"),
             "--days", "1", "--start-date", date],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    print(f"📅 Actualizando informe para {date}...")
    
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
            print(f"⚠️  Error al recolectar datos: {result.stderr}")
            return False
            
        # Cargar datos actualizados
        with open(data_file, 'r', encoding='utf-8') as f:
            updated_data = json.load(f)
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Comparar datos (ver si hay cambios significativos)
    old_news_count = len(report.get("data", {}).get("news", []))
    new_news_count = len(updated_data.get("news", []))
    
    old_events_count = len(report.get("data", {}).get("events", []))
    new_events_count = len(updated_data.get("events", []))
    
    has_changes = (
        old_news_count != new_news_count or
        old_events_count != new_events_count
    )
    
    if not has_changes:
        print("ℹ️  No hay cambios significativos en los datos")
        return True
    
    print(f"📊 Cambios detectados:")
    print(f"   Noticias: {old_news_count} → {new_news_count}")
    print(f"   Eventos: {old_events_count} → {new_events_count}")
    
    # Regenerar mensaje con datos actualizados
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
            print(f"⚠️  Error al generar mensaje: {result.stderr}")
            return False
            
        # Leer mensaje actualizado
        updated_message = message_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Actualizar informe
    report["data"] = updated_data
    report["message"] = updated_message
    report["status"] = "updated"
    report["updated_at"] = datetime.now().isoformat()
    
    # Guardar
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Actualizar base de datos de memoria
    try:
        from update_memory_db import update_memory_for_report
        update_memory_for_report(target_date)
    except:
        pass  # No crítico si falla
    
    print(f"✅ Informe actualizado: {report_file}")
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
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    print("🔄 Actualizando informe del día")
    print("=" * 50)
    print(f"📅 Fecha: {target_date}")
    print("")
    
    success = update_report_for_date(target_date)
    
    if success:
        print("")
        print("=" * 50)
        print("✅ Actualización completada")
    else:
        print("")
        print("=" * 50)
        print("❌ Error en la actualización")
        sys.exit(1)


if __name__ == "__main__":
    main()

