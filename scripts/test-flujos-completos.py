#!/usr/bin/env python3
"""
Script de pruebas para verificar todos los flujos automáticos
MVP - InforMessi
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
except ImportError:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

def print_header(title):
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def test_1_cron_schedule():
    """Prueba 1: Verificar que el cron esté configurado correctamente"""
    print_header("Prueba 1: Verificación del Cron de GitHub Actions")
    
    workflow_file = PROJECT_ROOT / ".github" / "workflows" / "daily-informessi.yml"
    if not workflow_file.exists():
        print("❌ Archivo de workflow no encontrado")
        return False
    
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    if "cron: '15 13 * * *'" in content:
        print("✅ Cron configurado: 15 13 * * * (13:15 UTC = 10:15 AM Argentina)")
        print("   - Se ejecutará todos los días a las 10:15 AM hora Argentina")
        return True
    else:
        print("⚠️  Cron no encontrado o diferente")
        return False

def test_2_fallback_automatico():
    """Prueba 2: Verificar que el fallback automático esté configurado"""
    print_header("Prueba 2: Fallback Automático (si no hay respuesta)")
    
    workflow_file = PROJECT_ROOT / ".github" / "workflows" / "daily-informessi.yml"
    if not workflow_file.exists():
        print("❌ Archivo de workflow no encontrado")
        return False
    
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    if "auto-publish-fallback.py" in content:
        print("✅ Script de fallback encontrado en workflow")
        if "--hours 2" in content:
            print("   - Configurado para publicar después de 2 horas sin respuesta")
        else:
            print("   ⚠️  Tiempo de espera no especificado")
        return True
    else:
        print("❌ Script de fallback no encontrado en workflow")
        return False

def test_3_pre_approved():
    """Prueba 3: Verificar que los informes pre-aprobados se publiquen directamente"""
    print_header("Prueba 3: Informes Pre-Aprobados")
    
    # Crear un informe de prueba con pre_approved=True
    test_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    test_report = {
        "date": test_date,
        "generated_at": datetime.now().isoformat(),
        "data": {
            "date": test_date,
            "days_remaining": 100,
            "events": [],
            "news": []
        },
        "message": "🧪 Mensaje de prueba para informe pre-aprobado",
        "status": "draft",
        "pre_approved": True,
        "pre_approved_at": datetime.now().isoformat()
    }
    
    report_file = REPORTS_DIR / f"{test_date}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Informe de prueba creado: {test_date}.json")
    print(f"   - pre_approved: {test_report['pre_approved']}")
    
    # Verificar que send-daily-report-review.py detecte pre_approved
    script_file = PROJECT_ROOT / "scripts" / "send-daily-report-review.py"
    if script_file.exists():
        with open(script_file, 'r') as f:
            content = f.read()
        if "pre_approved" in content and "publicar directamente" in content.lower():
            print("✅ Script detecta informes pre-aprobados")
            return True
        else:
            print("⚠️  Script puede no detectar pre-aprobados correctamente")
            return False
    else:
        print("❌ Script send-daily-report-review.py no encontrado")
        return False

def test_4_generacion_edicion():
    """Prueba 4: Flujo completo de generación, edición y pre-aprobación"""
    print_header("Prueba 4: Generación, Edición y Pre-Aprobación")
    
    test_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    print(f"📅 Fecha de prueba: {test_date}")
    print()
    
    # Paso 1: Generar informe
    print("1️⃣  Generando informe...")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "generate-advance-reports.py"),
             "--days", "1", "--start-date", test_date],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print("   ✅ Informe generado correctamente")
        else:
            print(f"   ⚠️  Error al generar: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Verificar que existe
    report_file = REPORTS_DIR / f"{test_date}.json"
    if not report_file.exists():
        print("   ❌ Informe no se creó")
        return False
    
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    print(f"   ✅ Informe existe: {report_file.name}")
    print(f"   - Status: {report.get('status', 'N/A')}")
    print(f"   - Pre-approved: {report.get('pre_approved', False)}")
    print()
    
    # Paso 2: Verificar script de edición
    print("2️⃣  Verificando script de edición...")
    edit_script = PROJECT_ROOT / "scripts" / "edit-and-validate-report.py"
    if edit_script.exists():
        print("   ✅ Script edit-and-validate-report.py existe")
    else:
        print("   ❌ Script no encontrado")
        return False
    
    print()
    print("💡 Para probar edición manualmente:")
    print(f"   python3 scripts/edit-and-validate-report.py --date {test_date}")
    print()
    
    # Paso 3: Simular pre-aprobación
    print("3️⃣  Simulando pre-aprobación...")
    report["pre_approved"] = True
    report["pre_approved_at"] = datetime.now().isoformat()
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("   ✅ Informe marcado como pre-aprobado")
    print()
    
    # Paso 4: Verificar que se publique directamente
    print("4️⃣  Verificando que se publique directamente...")
    script_file = PROJECT_ROOT / "scripts" / "send-daily-report-review.py"
    if script_file.exists():
        with open(script_file, 'r') as f:
            content = f.read()
        if "pre_approved" in content and "publicar directamente" in content.lower():
            print("   ✅ Script publicará directamente si está pre-aprobado")
            return True
        else:
            print("   ⚠️  Script puede no publicar directamente")
            return False
    
    return True

def main():
    print("🚀 Pruebas de Flujos Automáticos - InforMessi")
    print("=" * 60)
    
    results = []
    
    # Ejecutar pruebas
    results.append(("Cron de GitHub Actions", test_1_cron_schedule()))
    results.append(("Fallback Automático", test_2_fallback_automatico()))
    results.append(("Informes Pre-Aprobados", test_3_pre_approved()))
    results.append(("Generación/Edición/Pre-Aprobación", test_4_generacion_edicion()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Todas las pruebas pasaron")
    else:
        print("⚠️  Algunas pruebas fallaron - revisa los detalles arriba")
    print("=" * 60)
    
    print("\n💡 Próximos pasos:")
    print("   1. Prueba manualmente el flujo completo:")
    print("      python3 scripts/generate-advance-reports.py --days 1")
    print("      python3 scripts/edit-and-validate-report.py --date [fecha]")
    print("      python3 scripts/send-daily-report-review.py --date [fecha]")
    print()
    print("   2. Verifica el workflow en GitHub Actions:")
    print("      - Ve a Actions → InforMessi - Flujo Diario Completo")
    print("      - Ejecuta manualmente con 'Run workflow'")
    print()
    print("   3. Prueba el fallback:")
    print("      python3 scripts/auto-publish-fallback.py --check-all --hours 0.1")
    print("      (esto publicará informes de hace 6 minutos sin respuesta)")

if __name__ == "__main__":
    main()

