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
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = None) -> Dict:
        """Envía un mensaje a Telegram"""
        url = f"{self.base_url}/sendMessage"
        
        # Validar longitud del mensaje
        if len(text) > 4096:
            text = text[:4096] + "\n\n[Mensaje truncado...]"
        
        data = {
            "chat_id": chat_id,
            "text": text
        }
        
        # Solo agregar parse_mode si se especifica
        if parse_mode:
            data["parse_mode"] = parse_mode
        
        # Intentar enviar, si falla con HTML, intentar sin parse_mode
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Si falla y tenía parse_mode, intentar sin él
            if parse_mode:
                try:
                    data.pop("parse_mode", None)
                    response = requests.post(url, json=data, timeout=10)
                    response.raise_for_status()
                    return response.json()
                except Exception as e2:
                    # Obtener detalles del error
                    error_detail = ""
                    try:
                        if hasattr(e2, 'response') and e2.response:
                            error_response = e2.response.json()
                            error_detail = f" - {error_response.get('description', '')}"
                    except:
                        pass
                    raise Exception(f"Error al enviar mensaje: {str(e2)}{error_detail}")
            else:
                # Si ya estaba sin parse_mode, mostrar error completo
                error_detail = ""
                try:
                    if hasattr(e, 'response') and e.response:
                        error_response = e.response.json()
                        error_detail = f" - {error_response.get('description', '')}"
                except:
                    pass
                raise Exception(f"Error al enviar mensaje: {str(e)}{error_detail}")
    
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


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud para verificar que el servidor está activo"""
    return jsonify({
        'status': 'ok',
        'service': 'InforMessi Webhook',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """Maneja los webhooks de Telegram"""
    # Log de que se recibió una request
    print(f"📨 Request recibida: {request.method} a /webhook")
    print(f"   Headers: {dict(request.headers)}")
    
    if request.method == 'GET':
        # Telegram verifica el webhook con GET
        return jsonify({'ok': True, 'method': 'GET'})
    
    try:
        update = request.get_json()
        
        if not update:
            print("⚠️  Request sin JSON body")
            return jsonify({'ok': False, 'error': 'No JSON body'}), 400
        
        print(f"📦 Update recibido: {list(update.keys())}")
        
        # Log para debugging (sin información sensible)
        if 'callback_query' in update:
            callback = update['callback_query']
            data = callback.get('data', '')
            print(f"📥 Callback recibido: {data[:50]}...")
        
        # Verificar si es un callback query (botón presionado)
        if 'callback_query' in update:
            callback = update['callback_query']
            data = callback['data']
            query_id = callback['id']
            chat_id = str(callback['message']['chat']['id'])
            
            print(f"🔔 Callback query recibido: {data}")
            print(f"   Chat ID: {chat_id}")
            
            # Inicializar bot
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not token:
                print("❌ TELEGRAM_BOT_TOKEN no configurado")
                return jsonify({'ok': False, 'error': 'Token no configurado'}), 500
            
            bot = TelegramBot(token)
            
            # Responder al callback
            bot.answer_callback_query(query_id, "Procesando...")
            
            # Procesar acción
            if data.startswith('approve:'):
                print("✅ Procesando aprobación...")
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
                print(f"🔍 TELEGRAM_PUBLIC_CHAT_ID: {'Configurado' if public_chat_id else 'NO CONFIGURADO'}")
                
                if not public_chat_id:
                    error_msg = "⚠️ TELEGRAM_PUBLIC_CHAT_ID no configurado en Render"
                    print(f"❌ {error_msg}")
                    bot.send_message(chat_id, error_msg)
                    return jsonify({'ok': True})
                
                # Validar chat_id
                public_chat_id = str(public_chat_id).strip()
                print(f"📋 Public Chat ID: {public_chat_id[:20]}... (longitud: {len(public_chat_id)})")
                
                if not public_chat_id or public_chat_id == 'None':
                    error_msg = "⚠️ TELEGRAM_PUBLIC_CHAT_ID está vacío o inválido"
                    print(f"❌ {error_msg}")
                    bot.send_message(chat_id, error_msg)
                    return jsonify({'ok': True})
                
                try:
                    print(f"📤 Intentando publicar en grupo público (Chat ID: {public_chat_id})...")
                    # Publicar sin parse_mode para evitar problemas
                    publish_message(bot, public_chat_id, report['message'])
                    print("✅ Mensaje publicado exitosamente")
                    
                    # Actualizar informe: marcar como publicado
                    report['status'] = 'published'
                    report['published_at'] = datetime.now().isoformat()
                    
                    # Guardar informe actualizado
                    report_file = REPORTS_DIR / f"{today}.json"
                    with open(report_file, 'w', encoding='utf-8') as f:
                        json.dump(report, f, indent=2, ensure_ascii=False)
                    
                    # Actualizar base de datos de memoria
                    try:
                        from update_memory_db import update_memory_for_report
                        update_memory_for_report(today)
                    except:
                        pass
                    
                    bot.send_message(
                        chat_id,
                        "✅ Informe publicado en el grupo público"
                    )
                except Exception as e:
                    # Obtener más detalles del error
                    error_msg = str(e)
                    error_detail = ""
                    error_code = ""
                    try:
                        if hasattr(e, 'response') and e.response:
                            error_response = e.response.json()
                            error_detail = error_response.get('description', '')
                            error_code = error_response.get('error_code', '')
                    except:
                        pass
                    
                    # Log del error
                    print(f"❌ Error al publicar: {error_msg}")
                    if error_detail:
                        print(f"   Detalle: {error_detail}")
                    if error_code:
                        print(f"   Código: {error_code}")
                    
                    # Mensaje de error detallado
                    error_notification = (
                        f"❌ Error al publicar:\n"
                        f"Error: {error_msg}\n"
                    )
                    if error_detail:
                        error_notification += f"Detalle Telegram: {error_detail}\n"
                    if error_code:
                        error_notification += f"Código: {error_code}\n"
                    
                    error_notification += (
                        f"\n💡 Verifica:\n"
                        f"- Que el bot esté en el grupo público\n"
                        f"- Que el bot tenga permisos para enviar mensajes\n"
                        f"- Que TELEGRAM_PUBLIC_CHAT_ID sea correcto ({public_chat_id[:20]}...)\n"
                        f"- Que el chat_id sea un número (negativo para grupos)"
                    )
                    
                    try:
                        bot.send_message(chat_id, error_notification)
                    except:
                        print(f"❌ Error crítico: {error_msg} - {error_detail}")
                
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
                preview_text = (
                    f"✏️ Modo Edición\n\n"
                    f"Envía el mensaje editado como respuesta a este mensaje.\n\n"
                    f"Mensaje actual:\n{report['message'][:200]}...\n\n"
                    f"Envía tu versión editada ahora:"
                )
                bot.send_message(chat_id, preview_text)
                
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
                    if not public_chat_id:
                        bot.send_message(
                            chat_id,
                            "⚠️ TELEGRAM_PUBLIC_CHAT_ID no configurado en Render"
                        )
                        return jsonify({'ok': True})
                    
                    # Validar chat_id
                    public_chat_id = str(public_chat_id).strip()
                    if not public_chat_id or public_chat_id == 'None':
                        bot.send_message(
                            chat_id,
                            "⚠️ TELEGRAM_PUBLIC_CHAT_ID está vacío o inválido"
                        )
                        return jsonify({'ok': True})
                    
                    try:
                        # Publicar sin parse_mode para evitar problemas con HTML
                        publish_message(bot, public_chat_id, text)
                        
                        # Actualizar informe: marcar como publicado
                        report['status'] = 'published'
                        report['published_at'] = datetime.now().isoformat()
                        
                        # Guardar informe actualizado
                        with open(report_file, 'w', encoding='utf-8') as f:
                            json.dump(report, f, indent=2, ensure_ascii=False)
                        
                        # Actualizar base de datos de memoria
                        try:
                            from update_memory_db import update_memory_for_report
                            update_memory_for_report(today)
                        except:
                            pass
                        
                        bot.send_message(
                            chat_id,
                            "✅ Mensaje editado y publicado en el grupo público"
                        )
                    except Exception as e:
                        # Obtener más detalles del error
                        error_msg = str(e)
                        error_detail = ""
                        error_code = ""
                        try:
                            if hasattr(e, 'response') and e.response:
                                error_response = e.response.json()
                                error_detail = error_response.get('description', '')
                                error_code = error_response.get('error_code', '')
                        except:
                            pass
                        
                        # Mensaje de error detallado
                        error_notification = (
                            f"❌ Error al publicar:\n"
                            f"Error: {error_msg}\n"
                        )
                        if error_detail:
                            error_notification += f"Detalle Telegram: {error_detail}\n"
                        if error_code:
                            error_notification += f"Código: {error_code}\n"
                        
                        error_notification += (
                            f"\n💡 Verifica:\n"
                            f"- Que el mensaje no exceda 4096 caracteres ({len(text)} chars)\n"
                            f"- Que el bot esté en el grupo público\n"
                            f"- Que el bot tenga permisos para enviar mensajes\n"
                            f"- Que TELEGRAM_PUBLIC_CHAT_ID sea correcto ({public_chat_id[:20]}...)\n"
                            f"- Que el chat_id sea un número (negativo para grupos)"
                        )
                        
                        try:
                            bot.send_message(chat_id, error_notification)
                        except:
                            print(f"Error crítico: {error_msg} - {error_detail}")
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


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

