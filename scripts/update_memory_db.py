#!/usr/bin/env python3
"""
Actualiza la base de datos de memoria cuando se genera o actualiza un informe
MVP - InforMessi
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

def update_memory_for_report(date: str):
    """Actualiza la base de datos de memoria para un informe específico"""
    try:
        from rag_memory_database import MemoryDatabase
        
        report_file = REPORTS_DIR / f"{date}.json"
        if not report_file.exists():
            return False
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        db = MemoryDatabase()
        db.analyze_report(report)
        
        return True
    except Exception as e:
        print(f"⚠️  Error al actualizar memoria: {e}")
        return False


if __name__ == "__main__":
    from datetime import datetime
    
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    update_memory_for_report(target_date)

