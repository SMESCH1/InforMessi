#!/usr/bin/env python3
"""
Envía el informe del día al chat de revisión (privado)
Solo el usuario ve este mensaje para aprobar/rechazar
MVP - InforMessi
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from time_utils import now_ar_iso, today_ar

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # Si no hay python-dotenv, intentar cargar manualmente
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


def build_eval_warning_header(report: dict) -> str:
    """Arma el header de advertencia a prependear al texto del preview cuando
    report["eval_warning"] es True. Resume los checks de severity=error que
    fallaron en report["eval"]["checks"]."""
    eval_block = report.get("eval") or {}
    checks = eval_block.get("checks") or []
    failed_errors = [c for c in checks if not c.get("passed") and c.get("severity") == "error"]

    if failed_errors:
        detalle = "\n".join(f"- {c['name']}: {c['detail']}" for c in failed_errors)
    else:
        detalle = "- (ver reports/<fecha>.json → eval para el detalle)"

    return f"⚠️ EVALS FALLARON — revisar antes de aprobar:\n{detalle}\n\n---\n\n"


def load_report(date: str) -> dict:
    """Carga un informe desde reports/"""
    report_file = REPORTS_DIR / f"{date}.json"
    
    if not report_file.exists():
        print(f"❌ Informe para {date} no encontrado")
        print(f"   Ubicación esperada: {report_file}")
        sys.exit(1)
    
    with open(report_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def send_to_review_chat(message: str, preview_chat_id: str, token: str, media_path: str = None):
    """Envía mensaje al chat de revisión usando telegram-preview.py"""
    import subprocess
    
    cmd = [
        sys.executable, str(PROJECT_ROOT / "scripts" / "telegram-preview.py"),
        "--message", message,
        "--preview-chat-id", preview_chat_id,
        "--token", token,
        "--no-wait"  # No esperar respuesta automáticamente
    ]
    
    if media_path:
        cmd.extend(["--media", media_path])
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    
    return result.returncode == 0


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Envía el informe del día al chat de revisión (privado)"
    )
    parser.add_argument(
        "--date",
        help="Fecha a enviar (YYYY-MM-DD). Default: hoy"
    )
    
    args = parser.parse_args()
    
    if args.date:
        target_date = args.date
    else:
        target_date = today_ar()
    
    # Cargar variables de entorno
    preview_chat_id = os.getenv("TELEGRAM_PREVIEW_CHAT_ID")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not preview_chat_id or not token:
        print("❌ Variables de Telegram no configuradas")
        print("   Configura TELEGRAM_BOT_TOKEN y TELEGRAM_PREVIEW_CHAT_ID en .env")
        sys.exit(1)
    
    print("📤 Enviando informe al chat de revisión")
    print("=" * 50)
    print(f"📅 Fecha: {target_date}")
    print("")
    
    # Cargar informe
    report = load_report(target_date)
    message = report["message"]

    # Si los evals fallaron (eval_warning), prependear un header de alerta al
    # TEXTO DEL PREVIEW (no se toca report["message"] guardado en disco)
    if report.get("eval_warning"):
        message = build_eval_warning_header(report) + message
        print("⚠️  eval_warning activo: se antepone alerta al preview")

    # Detectar contenido audiovisual (antes de verificar pre-aprobación)
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    media_path = None
    try:
        from detect_media import get_media_for_date
        media = get_media_for_date(target_date)
        if media and media.get("primary_image"):
            media_path = str(PROJECT_ROOT / media["primary_image"])
            print(f"📷 Contenido visual detectado: {media['primary_image']}")
    except:
        media_path = None

    # Verificar si está pre-aprobado (nunca si los evals fallaron)
    if report.get("pre_approved") and not report.get("eval_warning"):
        print("✅ Informe pre-aprobado detectado")
        print("   Publicando directamente en grupo público...")
        print("")
        
        # Publicar directamente sin pasar por preview
        public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
        if not public_chat_id:
            print("⚠️  TELEGRAM_PUBLIC_CHAT_ID no configurado")
            print("   El informe está pre-aprobado pero no se puede publicar")
            sys.exit(1)
        
        # Importar función de publicación directamente
        import requests
        from pathlib import Path as PathLib
        
        def send_to_public_chat(message: str, public_chat_id: str, token: str, media_path: str = None):
            """Envía mensaje al grupo público de Telegram"""
            if media_path and PathLib(media_path).exists():
                # Enviar foto con mensaje como caption
                url = f"https://api.telegram.org/bot{token}/sendPhoto"
                try:
                    with open(media_path, 'rb') as photo:
                        files = {'photo': photo}
                        data = {
                            "chat_id": public_chat_id,
                            "caption": message
                        }
                        response = requests.post(url, files=files, data=data, timeout=30)
                        response.raise_for_status()
                        return True
                except Exception as e:
                    print(f"⚠️  Error al enviar foto: {e}, enviando solo texto")
                    return send_to_public_chat(message, public_chat_id, token, None)
            else:
                # Enviar solo texto
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {
                    "chat_id": public_chat_id,
                    "text": message
                }
                try:
                    response = requests.post(url, json=data, timeout=10)
                    response.raise_for_status()
                    return True
                except Exception as e:
                    print(f"❌ Error al publicar: {e}")
                    return False
        
        try:
            success = send_to_public_chat(message, public_chat_id, token, media_path)
            
            if success:
                # Marcar como publicado
                report["status"] = "published"
                report["published_at"] = now_ar_iso()
                
                report_file = REPORTS_DIR / f"{target_date}.json"
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                
                # Actualizar base de datos de memoria
                try:
                    from update_memory_db import update_memory_for_report
                    update_memory_for_report(target_date)
                except:
                    pass
                
                print("")
                print("=" * 50)
                print("✅ Informe pre-aprobado publicado directamente")
                print("=" * 50)
                sys.exit(0)
            else:
                print("❌ Error al publicar informe pre-aprobado")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error al publicar: {e}")
            sys.exit(1)
    
    # Enviar al chat de revisión (privado) solo si no está pre-aprobado
    print("📨 Enviando a chat de revisión (privado)...")
    success = send_to_review_chat(message, preview_chat_id, token, media_path)
    
    if success:
        print("")
        print("=" * 50)
        print("✅ Informe enviado al chat de revisión")
        print("")
        print("💡 Próximos pasos:")
        print("   1. Revisa el mensaje en tu chat privado de Telegram")
        print("   2. Usa los botones para aprobar/rechazar/editar")
        print("   3. Si apruebas, usa: python3 scripts/publish-approved-report.py --date", target_date)
    else:
        print("")
        print("=" * 50)
        print("❌ Error al enviar informe")
        sys.exit(1)


if __name__ == "__main__":
    main()

