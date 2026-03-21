#!/usr/bin/env python3
"""
Edita y valida un informe anticipadamente
Si está validado, no requerirá validación en preview
MVP - InforMessi
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"


def load_report(date: str) -> dict:
    """Carga un informe desde reports/"""
    report_file = REPORTS_DIR / f"{date}.json"
    
    if not report_file.exists():
        print(f"❌ Informe para {date} no encontrado")
        print(f"   Ubicación esperada: {report_file}")
        sys.exit(1)
    
    with open(report_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_report(date: str, report: dict):
    """Guarda un informe"""
    report_file = REPORTS_DIR / f"{date}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def edit_report_interactive(date: str):
    """Edita un informe de forma interactiva"""
    report = load_report(date)
    
    print("=" * 60)
    print(f"📝 Editando informe para {date}")
    print("=" * 60)
    print()
    print("Mensaje actual:")
    print("-" * 60)
    print(report.get("message", ""))
    print("-" * 60)
    print()
    
    print("Opciones:")
    print("  1. Editar mensaje")
    print("  2. Validar sin editar (marcar como pre-aprobado)")
    print("  3. Cancelar")
    print()
    
    choice = input("Selecciona opción (1-3): ").strip()
    
    if choice == "1":
        print()
        print("💡 Puedes editar el mensaje ahora.")
        print("   Presiona Enter para usar un editor externo, o escribe 'manual' para editar aquí.")
        print()
        edit_method = input("Método de edición [Enter=editor, manual=texto directo]: ").strip()
        
        if edit_method.lower() == "manual":
            print()
            print("Pega el mensaje editado (termina con línea vacía + Ctrl+D):")
            print()
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            new_message = "\n".join(lines).strip()
        else:
            # Usar editor externo
            import tempfile
            import subprocess
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(report.get("message", ""))
                temp_file = f.name
            
            # Abrir editor
            editor = os.getenv('EDITOR', 'nano')
            try:
                subprocess.run([editor, temp_file], check=True)
            except Exception as e:
                print(f"⚠️  Error al abrir editor: {e}")
                print("   Editando manualmente...")
                edit_method = "manual"
                print()
                print("Pega el mensaje editado (termina con línea vacía + Ctrl+D):")
                print()
                lines = []
                try:
                    while True:
                        line = input()
                        lines.append(line)
                except EOFError:
                    pass
                new_message = "\n".join(lines).strip()
            else:
                # Leer archivo editado
                with open(temp_file, 'r', encoding='utf-8') as f:
                    new_message = f.read().strip()
                
                # Eliminar archivo temporal
                os.unlink(temp_file)
        
        if new_message and new_message != report.get("message", ""):
            report["message"] = new_message
            report["status"] = "updated"
            report["updated_at"] = datetime.now().isoformat()
            report["edited_manually"] = True
            report["edited_at"] = datetime.now().isoformat()
            
            print()
            print("✅ Mensaje actualizado")
            print()
            
            # Preguntar si validar
            validate = input("¿Marcar como pre-aprobado? (s/n): ").strip().lower()
            if validate == "s":
                report["pre_approved"] = True
                report["pre_approved_at"] = datetime.now().isoformat()
                print("✅ Informe marcado como pre-aprobado")
            else:
                report["pre_approved"] = False
                print("ℹ️  Informe actualizado pero no pre-aprobado")
        else:
            print("⚠️  No se realizaron cambios")
            return False
        
    elif choice == "2":
        report["pre_approved"] = True
        report["pre_approved_at"] = datetime.now().isoformat()
        print("✅ Informe marcado como pre-aprobado")
        
    elif choice == "3":
        print("❌ Cancelado")
        return False
    else:
        print("❌ Opción inválida")
        return False
    
    # Guardar informe
    save_report(date, report)
    print()
    print("=" * 60)
    print("✅ Informe guardado")
    print("=" * 60)
    print()
    print(f"📁 Ubicación: {REPORTS_DIR / f'{date}.json'}")
    print()
    
    if report.get("pre_approved"):
        print("💡 Este informe será publicado automáticamente sin pasar por preview")
    else:
        print("💡 Este informe requerirá validación en preview")
    
    return True


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Edita y valida un informe anticipadamente"
    )
    parser.add_argument(
        "--date",
        help="Fecha a editar/validar (YYYY-MM-DD). Default: hoy"
    )
    
    args = parser.parse_args()
    
    if args.date:
        target_date = args.date
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    success = edit_report_interactive(target_date)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()




