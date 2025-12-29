#!/usr/bin/env python3
"""
Edita el mensaje de un informe de forma interactiva
Automáticamente cambia el status a "updated"
"""

import json
import sys
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"


def edit_report(date: str, editor: str = None):
    """Edita el mensaje de un informe"""
    report_file = REPORTS_DIR / f"{date}.json"
    
    if not report_file.exists():
        print(f"❌ Informe para {date} no encontrado")
        print(f"   Ubicación: {report_file}")
        sys.exit(1)
    
    # Cargar informe
    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    current_message = report.get("message", "")
    
    # Crear archivo temporal con el mensaje
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp:
        tmp.write(current_message)
        tmp_path = tmp.name
    
    # Determinar editor
    if editor:
        editor_cmd = editor
    else:
        # Intentar detectar editor preferido
        editors = ['nano', 'vim', 'vi', 'code', 'gedit']
        editor_cmd = None
        for ed in editors:
            if subprocess.run(['which', ed], capture_output=True).returncode == 0:
                editor_cmd = ed
                break
        
        if not editor_cmd:
            print("❌ No se encontró ningún editor. Usa --editor para especificar uno.")
            sys.exit(1)
    
    # Abrir editor
    print(f"📝 Editando mensaje para {date}")
    print(f"   Editor: {editor_cmd}")
    print(f"   Archivo temporal: {tmp_path}")
    print()
    print("💡 Instrucciones:")
    print("   - Edita el mensaje en el editor")
    print("   - Guarda y cierra el editor")
    print("   - El informe se actualizará automáticamente")
    print()
    
    try:
        # Ejecutar editor
        if editor_cmd == 'code':
            # VS Code necesita flag especial
            subprocess.run([editor_cmd, '--wait', tmp_path])
        else:
            subprocess.run([editor_cmd, tmp_path])
        
        # Leer mensaje editado
        with open(tmp_path, 'r', encoding='utf-8') as f:
            edited_message = f.read().strip()
        
        # Verificar si hubo cambios
        if edited_message == current_message:
            print("ℹ️  No se detectaron cambios. El informe no se actualizará.")
            return
        
        # Actualizar informe
        report["message"] = edited_message
        report["status"] = "updated"
        report["updated_at"] = datetime.now().isoformat()
        
        # Guardar
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print()
        print("✅ Informe actualizado exitosamente")
        print(f"   Archivo: {report_file}")
        print(f"   Status: updated")
        print(f"   Palabras: {len(edited_message.split())}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Edición cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        # Limpiar archivo temporal
        try:
            Path(tmp_path).unlink()
        except:
            pass


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Edita el mensaje de un informe"
    )
    parser.add_argument(
        "--date",
        help="Fecha a editar (YYYY-MM-DD). Default: hoy"
    )
    parser.add_argument(
        "--editor",
        help="Editor a usar (nano, vim, code, etc.). Default: auto-detecta"
    )
    
    args = parser.parse_args()
    
    if args.date:
        target_date = args.date
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    edit_report(target_date, args.editor)


if __name__ == "__main__":
    main()

