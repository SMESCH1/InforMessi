#!/usr/bin/env python3
"""
Publica un informe aprobado al grupo público de Telegram
Solo se ejecuta después de que el usuario aprueba en el chat privado
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


def send_to_public_chat(message: str, public_chat_id: str, token: str, media_path: str = None):
    """Envía mensaje al grupo público de Telegram"""
    import requests
    from pathlib import Path
    
    if media_path and Path(media_path).exists():
        # Enviar foto con mensaje como caption
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        try:
            with open(media_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    "chat_id": public_chat_id,
                    "caption": message,
                    "parse_mode": "HTML"
                }
                response = requests.post(url, files=files, data=data, timeout=30)
                response.raise_for_status()
                print(f"✅ Foto publicada en grupo público: {Path(media_path).name}")
                return True
        except Exception as e:
            print(f"⚠️  Error al enviar foto: {e}, enviando solo texto")
            # Fallback a texto
            return send_to_public_chat(message, public_chat_id, token, None)
    else:
        # Enviar solo texto
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": public_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            print("✅ Mensaje publicado en grupo público")
            return True
        except Exception as e:
            print(f"❌ Error al publicar: {e}")
            return False


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Publica un informe aprobado al grupo público de Telegram"
    )
    parser.add_argument(
        "--date",
        help="Fecha a publicar (YYYY-MM-DD). Default: hoy"
    )
    
    args = parser.parse_args()
    
    if args.date:
        target_date = args.date
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    # Cargar variables de entorno
    public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not public_chat_id or not token:
        print("❌ Variables de Telegram no configuradas")
        print("   Configura TELEGRAM_BOT_TOKEN y TELEGRAM_PUBLIC_CHAT_ID en .env")
        sys.exit(1)
    
    print("📤 Publicando informe aprobado al grupo público")
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
    
    # Enviar al grupo público
    print("📨 Publicando en grupo público...")
    success = send_to_public_chat(message, public_chat_id, token, media_path)
    
    if success:
        # Marcar como publicado
        report["status"] = "published"
        report["published_at"] = datetime.now().isoformat()
        
        report_file = REPORTS_DIR / f"{target_date}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Actualizar base de datos de memoria
        try:
            from update_memory_db import update_memory_for_report
            update_memory_for_report(target_date)
        except:
            pass  # No crítico si falla
        
        print("")
        print("=" * 50)
        print("✅ Informe publicado y marcado como publicado")
    else:
        print("")
        print("=" * 50)
        print("❌ Error al publicar informe")
        sys.exit(1)


if __name__ == "__main__":
    main()

