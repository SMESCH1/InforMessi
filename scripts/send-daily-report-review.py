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
        target_date = datetime.now().strftime("%Y-%m-%d")
    
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
    
    # Detectar contenido audiovisual
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    try:
        from detect_media import get_media_for_date
        media = get_media_for_date(target_date)
        media_path = None
        if media and media.get("primary_image"):
            media_path = str(PROJECT_ROOT / media["primary_image"])
            print(f"📷 Contenido visual detectado: {media['primary_image']}")
    except:
        media_path = None
    
    # Enviar al chat de revisión (privado)
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

