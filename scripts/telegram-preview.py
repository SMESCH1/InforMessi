#!/usr/bin/env python3
"""
Script de preview y revisión humana en Telegram
Fase 3 - InforMessi
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict

try:
    import requests
except ImportError:
    print("ERROR: Necesitas instalar 'requests': pip install requests")
    sys.exit(1)

# Configuración
PROJECT_ROOT = Path(__file__).parent.parent

class TelegramBot:
    """Clase para interactuar con Telegram Bot API"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    def send_message(self, chat_id: str, text: str, reply_markup: Optional[Dict] = None) -> Dict:
        """Envía un mensaje a Telegram"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def send_message_with_buttons(self, chat_id: str, text: str, buttons: list) -> Dict:
        """Envía un mensaje con botones inline"""
        keyboard = {
            "inline_keyboard": [[button] for button in buttons]
        }
        return self.send_message(chat_id, text, keyboard)
    
    def get_updates(self, offset: Optional[int] = None, timeout: int = 10) -> Dict:
        """Obtiene actualizaciones del bot"""
        url = f"{self.base_url}/getUpdates"
        params = {"timeout": timeout}
        if offset:
            params["offset"] = offset
        
        response = requests.get(url, params=params, timeout=timeout + 5)
        response.raise_for_status()
        return response.json()
    
    def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None) -> Dict:
        """Responde a una query de callback"""
        url = f"{self.base_url}/answerCallbackQuery"
        data = {"callback_query_id": callback_query_id}
        if text:
            data["text"] = text
        
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()


def send_preview(bot: TelegramBot, chat_id: str, message: str, message_id: str) -> Dict:
    """Envía el mensaje generado para revisión con botones de acción"""
    
    preview_text = f"""<b>📨 PREVIEW - Mensaje Generado</b>

<i>ID: {message_id}</i>

{message}

<b>━━━━━━━━━━━━━━━━━━━━</b>
<i>Selecciona una acción:</i>"""
    
    buttons = [
        {"text": "✅ Aprobar", "callback_data": f"approve:{message_id}"},
        {"text": "❌ Rechazar", "callback_data": f"reject:{message_id}"},
        {"text": "✏️ Editar", "callback_data": f"edit:{message_id}"}
    ]
    
    return bot.send_message_with_buttons(chat_id, preview_text, buttons)


def wait_for_response(bot: TelegramBot, message_id: str, timeout: int = 3600) -> Optional[str]:
    """Espera la respuesta del usuario (aprobar/rechazar/editar)"""
    
    print(f"⏳ Esperando respuesta para mensaje {message_id}...")
    print(f"   (Timeout: {timeout} segundos)")
    
    start_time = time.time()
    last_update_id = None
    
    while time.time() - start_time < timeout:
        try:
            updates = bot.get_updates(offset=last_update_id, timeout=10)
            
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    last_update_id = update["update_id"] + 1
                    
                    # Verificar si es un callback query
                    if "callback_query" in update:
                        callback = update["callback_query"]
                        data = callback["data"]
                        query_id = callback["id"]
                        
                        # Verificar que sea para este mensaje
                        if message_id in data:
                            # Responder al callback
                            bot.answer_callback_query(query_id, "Procesando...")
                            
                            # Extraer acción
                            if data.startswith("approve:"):
                                return "approve"
                            elif data.startswith("reject:"):
                                return "reject"
                            elif data.startswith("edit:"):
                                return "edit"
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n⚠️  Interrumpido por el usuario")
            return None
        except Exception as e:
            print(f"⚠️  Error al obtener actualizaciones: {e}")
            time.sleep(5)
    
    print(f"⏱️  Timeout alcanzado ({timeout} segundos)")
    return None


def publish_message(bot: TelegramBot, chat_id: str, message: str) -> Dict:
    """Publica el mensaje aprobado en el canal público"""
    return bot.send_message(chat_id, message)


def send_photo(token: str, chat_id: str, caption: str, photo_path: str):
    """Envía una foto con caption a Telegram"""
    from pathlib import Path
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    photo_file = Path(photo_path)
    if not photo_file.exists():
        print(f"⚠️  Archivo no encontrado: {photo_path}, enviando solo texto")
        bot = TelegramBot(token)
        bot.send_message(chat_id, caption)
        return
    
    try:
        with open(photo_file, 'rb') as photo:
            files = {'photo': photo}
            data = {
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": "HTML"
            }
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            print(f"✅ Foto enviada a Telegram: {photo_file.name}")
            return response.json()
    except Exception as e:
        print(f"❌ Error al enviar foto: {e}")
        # Fallback: enviar solo texto
        bot = TelegramBot(token)
        bot.send_message(chat_id, caption)


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sistema de preview y revisión humana en Telegram"
    )
    parser.add_argument(
        "--message",
        required=True,
        help="Texto del mensaje generado"
    )
    parser.add_argument(
        "--message-id",
        default=None,
        help="ID único del mensaje (default: timestamp)"
    )
    parser.add_argument(
        "--preview-chat-id",
        required=True,
        help="Chat ID del canal de preview"
    )
    parser.add_argument(
        "--publish-chat-id",
        help="Chat ID del canal público (solo si se aprueba)"
    )
    parser.add_argument(
        "--token",
        help="Token del bot de Telegram (o usar TELEGRAM_BOT_TOKEN)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Timeout en segundos para esperar respuesta (default: 3600)"
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Solo enviar preview, no esperar respuesta"
    )
    parser.add_argument(
        "--media",
        help="Ruta a archivo de imagen/video para enviar junto con el mensaje"
    )
    
    args = parser.parse_args()
    
    # Obtener token
    token = args.token or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: Token de Telegram no encontrado")
        print("   Usa --token o configura TELEGRAM_BOT_TOKEN")
        sys.exit(1)
    
    # Generar message_id si no se proporciona
    message_id = args.message_id or str(int(time.time()))
    
    print("🚀 InforMessi - Sistema de Revisión Humana")
    print("=" * 50)
    
    # Inicializar bot
    bot = TelegramBot(token)
    
    # Enviar preview (con o sin media)
    print(f"📤 Enviando preview a chat {args.preview_chat_id}...")
    try:
        if args.media and Path(args.media).exists():
            # Enviar foto con mensaje como caption
            send_photo(token, args.preview_chat_id, args.message, args.media)
            print(f"   ✅ Preview con foto enviado")
        else:
            # Enviar solo texto
            result = send_preview(bot, args.preview_chat_id, args.message, message_id)
            preview_message_id = result["result"]["message_id"]
            print(f"   ✅ Preview enviado (mensaje ID: {preview_message_id})")
    except Exception as e:
        print(f"   ❌ Error al enviar preview: {e}")
        sys.exit(1)
    
    # Esperar respuesta si no es --no-wait
    if not args.no_wait:
        response = wait_for_response(bot, message_id, args.timeout)
        
        if response == "approve":
            print("\n✅ Mensaje aprobado")
            
            # Intentar publicar en grupo público si está configurado
            public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
            if public_chat_id:
                print(f"📤 Publicando en grupo público ({public_chat_id})...")
                try:
                    publish_message(bot, public_chat_id, args.message)
                    print("   ✅ Mensaje publicado en grupo público")
                except Exception as e:
                    print(f"   ❌ Error al publicar: {e}")
                    print("   ⚠️  Usa: python3 scripts/publish-approved-report.py para publicar manualmente")
            elif args.publish_chat_id:
                print(f"📤 Publicando en canal {args.publish_chat_id}...")
                try:
                    publish_message(bot, args.publish_chat_id, args.message)
                    print("   ✅ Mensaje publicado")
                except Exception as e:
                    print(f"   ❌ Error al publicar: {e}")
                    sys.exit(1)
            else:
                print("⚠️  No se especificó TELEGRAM_PUBLIC_CHAT_ID ni --publish-chat-id")
                print("   Usa: python3 scripts/publish-approved-report.py para publicar manualmente")
        
        elif response == "reject":
            print("\n❌ Mensaje rechazado")
            print("   El mensaje no será publicado")
        
        elif response == "edit":
            print("\n✏️  Mensaje marcado para edición")
            print("   Abriendo editor...")
            
            # Intentar abrir el editor automáticamente
            try:
                import subprocess
                from pathlib import Path
                
                # Obtener la fecha del mensaje (si está disponible en args)
                # Si no, usar la fecha de hoy
                from datetime import datetime
                target_date = datetime.now().strftime("%Y-%m-%d")
                
                # Si hay un archivo de reporte, abrirlo
                project_root = Path(__file__).parent.parent
                report_file = project_root / "reports" / f"{target_date}.json"
                
                if report_file.exists():
                    # Usar el script edit-report.py
                    edit_script = project_root / "scripts" / "edit-report.py"
                    subprocess.run([sys.executable, str(edit_script), "--date", target_date])
                    print("   ✅ Editor cerrado. Si guardaste cambios, el informe fue actualizado.")
                    print("   💡 Para publicar el informe editado:")
                    print(f"      python3 scripts/publish-approved-report.py --date {target_date}")
                else:
                    print("   ⚠️  No se encontró el archivo de informe para editar")
                    print("   💡 Edita el mensaje manualmente y luego publícalo")
            except Exception as e:
                print(f"   ⚠️  No se pudo abrir el editor automáticamente: {e}")
                print("   💡 Edita el mensaje manualmente y luego publícalo")
        
        elif response is None:
            print("\n⏱️  No se recibió respuesta (timeout o interrupción)")
            sys.exit(1)
    else:
        print("\n⚠️  Modo --no-wait: No se esperará respuesta")
        print("   Revisa el mensaje en Telegram y actúa manualmente")


if __name__ == "__main__":
    main()

