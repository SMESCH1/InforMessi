#!/usr/bin/env python3
"""
SOLUCIÓN RÁPIDA: Envía a preview y espera localmente la aprobación
Si el webhook no funciona, este script procesa los botones localmente
MVP - InforMessi
"""

import json
import os
import sys
from datetime import datetime
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

# Importar funciones de telegram-preview
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from telegram_preview import TelegramBot, send_preview, wait_for_response
from publish_approved_report import send_to_public_chat

def load_report(date: str) -> dict:
    """Carga un informe desde reports/"""
    report_file = REPORTS_DIR / f"{date}.json"
    
    if not report_file.exists():
        print(f"❌ Informe para {date} no encontrado")
        sys.exit(1)
    
    with open(report_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Envía a preview y espera aprobación localmente (solución rápida)"
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
    
    # Cargar variables
    preview_chat_id = os.getenv("TELEGRAM_PREVIEW_CHAT_ID")
    public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not all([preview_chat_id, public_chat_id, token]):
        print("❌ Variables de Telegram no configuradas")
        sys.exit(1)
    
    print("📤 Enviando informe a preview (esperando aprobación localmente)")
    print("=" * 60)
    print(f"📅 Fecha: {target_date}")
    print()
    
    # Cargar informe
    report = load_report(target_date)
    message = report["message"]
    
    # Verificar si está pre-aprobado
    if report.get("pre_approved"):
        print("✅ Informe pre-aprobado, publicando directamente...")
        success = send_to_public_chat(message, public_chat_id, token, None)
        if success:
            report["status"] = "published"
            report["published_at"] = datetime.now().isoformat()
            report_file = REPORTS_DIR / f"{target_date}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print("✅ Publicado directamente")
        sys.exit(0)
    
    # Inicializar bot
    bot = TelegramBot(token)
    
    # Generar ID único para el mensaje
    message_id = f"{target_date}-{datetime.now().strftime('%H%M%S')}"
    
    # Enviar preview
    print("📨 Enviando a chat de preview...")
    try:
        send_preview(bot, preview_chat_id, message, message_id)
        print("✅ Mensaje enviado a preview")
        print()
        print("⏳ Esperando tu respuesta en Telegram...")
        print("   (Presiona Aprobar/Rechazar/Editar en el chat privado)")
        print()
    except Exception as e:
        print(f"❌ Error al enviar: {e}")
        sys.exit(1)
    
    # Esperar respuesta
    response = wait_for_response(bot, message_id, timeout=3600)
    
    if response == "approve":
        print("\n✅ Aprobado! Publicando en grupo público...")
        try:
            success = send_to_public_chat(message, public_chat_id, token, None)
            if success:
                report["status"] = "published"
                report["published_at"] = datetime.now().isoformat()
                report_file = REPORTS_DIR / f"{target_date}.json"
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                
                # Actualizar memoria
                try:
                    from update_memory_db import update_memory_for_report
                    update_memory_for_report(target_date)
                except:
                    pass
                
                print("✅ Publicado en grupo público")
            else:
                print("❌ Error al publicar")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif response == "reject":
        print("\n❌ Rechazado. No se publicará.")
    
    elif response == "edit":
        print("\n✏️  Edición solicitada")
        print("   Envía el mensaje editado al bot en el chat privado...")
        
        from telegram_preview import wait_for_edited_message
        edited_message = wait_for_edited_message(bot, preview_chat_id, timeout=300)
        
        if edited_message:
            print("\n✅ Mensaje editado recibido. Publicando...")
            report["message"] = edited_message
            report["status"] = "updated"
            report["updated_at"] = datetime.now().isoformat()
            
            report_file = REPORTS_DIR / f"{target_date}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            try:
                success = send_to_public_chat(edited_message, public_chat_id, token, None)
                if success:
                    report["status"] = "published"
                    report["published_at"] = datetime.now().isoformat()
                    with open(report_file, 'w', encoding='utf-8') as f:
                        json.dump(report, f, indent=2, ensure_ascii=False)
                    
                    # Actualizar memoria
                    try:
                        from update_memory_db import update_memory_for_report
                        update_memory_for_report(target_date)
                    except:
                        pass
                    
                    print("✅ Mensaje editado publicado")
                else:
                    print("❌ Error al publicar mensaje editado")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("\n⏱️  Timeout esperando mensaje editado")
    
    else:
        print("\n⏱️  Timeout o cancelado")

if __name__ == "__main__":
    main()




