#!/usr/bin/env python3
"""
Envía el informe del día a Telegram
MVP - InforMessi
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar scripts al path para imports
sys.path.insert(0, str(Path(__file__).parent))

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


def send_to_telegram(message: str, preview_chat_id: str, token: str):
    """Envía mensaje a Telegram usando telegram-preview.py"""
    import subprocess
    
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "telegram-preview.py"),
         "--message", message,
         "--preview-chat-id", preview_chat_id,
         "--token", token,
         "--no-wait"],
        capture_output=True,
        text=True
    )
    
    return result.returncode == 0


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Envía el informe del día a Telegram"
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
    
    print("📤 Enviando informe del día")
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
    
    # Enviar
    print("📨 Enviando a Telegram...")
    success = send_to_telegram(message, preview_chat_id, token, media_path)
    
    if success:
        # Marcar como publicado
        report["status"] = "published"
        report["published_at"] = datetime.now().isoformat()
        
        report_file = REPORTS_DIR / f"{target_date}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("")
        print("=" * 50)
        print("✅ Informe enviado y marcado como publicado")
    else:
        print("")
        print("=" * 50)
        print("❌ Error al enviar informe")
        sys.exit(1)


if __name__ == "__main__":
    main()

