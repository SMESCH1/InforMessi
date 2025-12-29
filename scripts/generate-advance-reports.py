#!/usr/bin/env python3
"""
Genera informes con antelación (15 días por defecto)
MVP - InforMessi
"""

import json
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def generate_report_for_date(date: str) -> dict:
    """Genera un informe para una fecha específica"""
    print(f"📅 Generando informe para {date}...")
    
    # Recolectar datos
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
            return None
            
        # Cargar datos
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    # Generar mensaje
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
            return None
            
        # Leer mensaje
        message = message_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    # Guardar informe
    report = {
        "date": date,
        "generated_at": datetime.now().isoformat(),
        "data": data,
        "message": message,
        "status": "draft",  # draft, updated, published
        "updated_at": None,
        "published_at": None
    }
    
    report_file = REPORTS_DIR / f"{date}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Actualizar base de datos de memoria
    try:
        from update_memory_db import update_memory_for_report
        update_memory_for_report(date)
    except:
        pass  # No crítico si falla
    
    print(f"✅ Informe guardado: {report_file}")
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
    
    print("🚀 Generando informes con antelación")
    print("=" * 50)
    print(f"📅 Fecha inicio: {start_date.strftime('%Y-%m-%d')}")
    print(f"📊 Días a generar: {args.days}")
    print("")
    
    generated = 0
    failed = 0
    
    for i in range(args.days):
        target_date = start_date + timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        
        # Verificar si ya existe
        report_file = REPORTS_DIR / f"{date_str}.json"
        if report_file.exists():
            print(f"⏭️  Informe para {date_str} ya existe, omitiendo...")
            continue
        
        report = generate_report_for_date(date_str)
        if report:
            generated += 1
        else:
            failed += 1
        print("")
    
    print("=" * 50)
    print(f"✅ Informes generados: {generated}")
    if failed > 0:
        print(f"❌ Informes fallidos: {failed}")
    print(f"📁 Ubicación: {REPORTS_DIR}")


if __name__ == "__main__":
    main()

