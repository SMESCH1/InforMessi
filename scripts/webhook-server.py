#!/usr/bin/env python3
"""
Servidor webhook para Telegram Bot
Permite aprobación automática sin tener la PC prendida
MVP - InforMessi
"""

import os
import json
import sys
from pathlib import Path
from flask import Flask, request, jsonify
from datetime import datetime

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

app = Flask(__name__)

# Importar funciones de telegram-preview
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# Importar directamente las clases y funciones necesarias
import requests
from typing import Optional, Dict

class TelegramBot:
    """Clase para interactuar con Telegram Bot API"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = 'HTML') -> Dict:
        """Envía un mensaje a Telegram"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        response = requests.post(url, json=data, timeout=10)
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


def publish_message(bot: TelegramBot, chat_id: str, message: str) -> Dict:
    """Publica el mensaje aprobado en el canal público"""
    return bot.send_message(chat_id, message)


def load_report(date: str) -> dict:
    """Carga un informe desde reports/"""
    report_file = REPORTS_DIR / f"{date}.json"
    
    if not report_file.exists():
        return None
    
    with open(report_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@app.route('/webhook', methods=['POST'])
def webhook():
    """Maneja los webhooks de Telegram"""
    try:
        update = request.get_json()
        
        # Verificar si es un callback query (botón presionado)
        if 'callback_query' in update:
            callback = update['callback_query']
            data = callback['data']
            query_id = callback['id']
            chat_id = str(callback['message']['chat']['id'])
            
            # Inicializar bot
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not token:
                return jsonify({'ok': False, 'error': 'Token no configurado'}), 500
            
            bot = TelegramBot(token)
            
            # Responder al callback
            bot.answer_callback_query(query_id, "Procesando...")
            
            # Procesar acción
            if data.startswith('approve:'):
                message_id = data.split(':')[1]
                
                # Cargar informe del día
                today = datetime.now().strftime('%Y-%m-%d')
                report = load_report(today)
                
                if not report:
                    bot.send_message(
                        chat_id,
                        f"❌ No se encontró informe para {today}"
                    )
                    return jsonify({'ok': True})
                
                # Publicar en grupo público
                public_chat_id = os.getenv('TELEGRAM_PUBLIC_CHAT_ID')
                if public_chat_id:
                    try:
                        publish_message(bot, public_chat_id, report['message'])
                        bot.send_message(
                            chat_id,
                            "✅ Informe publicado en el grupo público"
                        )
                    except Exception as e:
                        bot.send_message(
                            chat_id,
                            f"❌ Error al publicar: {str(e)}"
                        )
                else:
                    bot.send_message(
                        chat_id,
                        "⚠️ TELEGRAM_PUBLIC_CHAT_ID no configurado"
                    )
                
                return jsonify({'ok': True})
            
            elif data.startswith('reject:'):
                bot.send_message(
                    chat_id,
                    "❌ Informe rechazado. No se publicará."
                )
                return jsonify({'ok': True})
            
            elif data.startswith('edit:'):
                message_id = data.split(':')[1]
                
                # Cargar informe del día
                today = datetime.now().strftime('%Y-%m-%d')
                report = load_report(today)
                
                if not report:
                    bot.send_message(
                        chat_id,
                        f"❌ No se encontró informe para {today}"
                    )
                    return jsonify({'ok': True})
                
                # Enviar mensaje pidiendo la versión editada
                bot.send_message(
                    chat_id,
                    f"✏️ <b>Modo Edición</b>\n\n"
                    f"Envía el mensaje editado como respuesta a este mensaje.\n\n"
                    f"<i>Mensaje actual:</i>\n{report['message'][:200]}...\n\n"
                    f"<b>Envía tu versión editada ahora:</b>",
                    parse_mode='HTML'
                )
                
                # Guardar estado de edición (en memoria por ahora)
                # En producción, usar Redis o base de datos
                return jsonify({'ok': True})
        
        # Verificar si es un mensaje de texto (respuesta a edición)
        elif 'message' in update and 'text' in update['message']:
            message = update['message']
            chat_id = str(message['chat']['id'])
            text = message['text']
            
            # Verificar si es respuesta a un mensaje de edición
            # (simplificado: si el chat es el privado y el texto es largo, asumimos que es edición)
            preview_chat_id = os.getenv('TELEGRAM_PREVIEW_CHAT_ID')
            
            if preview_chat_id and chat_id == preview_chat_id and len(text) > 50:
                token = os.getenv('TELEGRAM_BOT_TOKEN')
                if not token:
                    return jsonify({'ok': False}), 500
                
                bot = TelegramBot(token)
                
                # Cargar informe del día
                today = datetime.now().strftime('%Y-%m-%d')
                report = load_report(today)
                
                if report:
                    # Actualizar mensaje en el informe
                    report['message'] = text
                    report['status'] = 'updated'
                    report['updated_at'] = datetime.now().isoformat()
                    
                    # Guardar informe
                    report_file = REPORTS_DIR / f"{today}.json"
                    with open(report_file, 'w', encoding='utf-8') as f:
                        json.dump(report, f, indent=2, ensure_ascii=False)
                    
                    # Publicar automáticamente en grupo público
                    public_chat_id = os.getenv('TELEGRAM_PUBLIC_CHAT_ID')
                    if public_chat_id:
                        try:
                            publish_message(bot, public_chat_id, text)
                            bot.send_message(
                                chat_id,
                                "✅ Mensaje editado y publicado en el grupo público"
                            )
                        except Exception as e:
                            bot.send_message(
                                chat_id,
                                f"❌ Error al publicar: {str(e)}"
                            )
                    else:
                        bot.send_message(
                            chat_id,
                            "✅ Mensaje editado guardado. ⚠️ TELEGRAM_PUBLIC_CHAT_ID no configurado para publicar."
                        )
                else:
                    bot.send_message(
                        chat_id,
                        f"❌ No se encontró informe para {today}"
                    )
            
            return jsonify({'ok': True})
        
        return jsonify({'ok': True})
    
    except Exception as e:
        print(f"Error en webhook: {e}", file=sys.stderr)
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud para verificar que el servidor está activo"""
    return jsonify({
        'status': 'ok',
        'service': 'InforMessi Webhook',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

