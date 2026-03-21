#!/usr/bin/env python3
"""
Diagnóstico del workflow de GitHub Actions
Verifica configuración y posibles problemas
MVP - InforMessi
"""

import os
import sys
import requests
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

def check_telegram_config():
    """Verifica configuración de Telegram"""
    print("🔍 Verificando configuración de Telegram...")
    print("=" * 50)
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    preview_chat_id = os.getenv("TELEGRAM_PREVIEW_CHAT_ID")
    public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
    
    # Verificar token
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        return False
    else:
        print(f"✅ TELEGRAM_BOT_TOKEN: {'*' * 20}...{token[-10:]}")
    
    # Verificar preview chat ID
    if not preview_chat_id:
        print("❌ TELEGRAM_PREVIEW_CHAT_ID no configurado")
        return False
    else:
        preview_chat_id = str(preview_chat_id).strip()
        print(f"✅ TELEGRAM_PREVIEW_CHAT_ID: {preview_chat_id}")
        print(f"   Tipo: {'Grupo' if preview_chat_id.startswith('-') else 'Chat privado'}")
        print(f"   Longitud: {len(preview_chat_id)} caracteres")
    
    # Verificar public chat ID
    if not public_chat_id:
        print("⚠️  TELEGRAM_PUBLIC_CHAT_ID no configurado (opcional para revisión)")
    else:
        public_chat_id = str(public_chat_id).strip()
        print(f"✅ TELEGRAM_PUBLIC_CHAT_ID: {public_chat_id}")
        print(f"   Tipo: {'Grupo' if public_chat_id.startswith('-') else 'Chat privado'}")
        print(f"   Longitud: {len(public_chat_id)} caracteres")
    
    return True


def test_telegram_connection(token: str, chat_id: str, chat_name: str, send_test: bool = False):
    """Verifica conexión con Telegram (sin enviar mensaje por defecto)"""
    print(f"\n🔍 Verificando conexión con {chat_name}...")
    print("-" * 50)
    
    # Solo verificar que el bot puede acceder a la API, sin enviar mensaje
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            bot_info = result.get('result', {})
            print(f"✅ Bot verificado: @{bot_info.get('username', 'N/A')}")
            print(f"   Nombre: {bot_info.get('first_name', 'N/A')}")
            
            # Verificar que el chat existe (sin enviar mensaje)
            url_chat = f"https://api.telegram.org/bot{token}/getChat"
            chat_data = {"chat_id": chat_id}
            chat_response = requests.post(url_chat, json=chat_data, timeout=10)
            
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                if chat_result.get("ok"):
                    chat_info = chat_result.get('result', {})
                    print(f"✅ Chat verificado: {chat_info.get('title', chat_info.get('first_name', 'N/A'))}")
                    print(f"   Tipo: {chat_info.get('type', 'N/A')}")
                    
                    # Solo enviar mensaje de prueba si se solicita explícitamente
                    if send_test:
                        return send_test_message(token, chat_id, chat_name)
                    else:
                        return True
                else:
                    error_desc = chat_result.get('description', 'Unknown error')
                    print(f"⚠️  No se pudo verificar el chat: {error_desc}")
                    return False
            else:
                print(f"⚠️  No se pudo verificar el chat (status: {chat_response.status_code})")
                return False
        else:
            print(f"❌ Error al verificar bot: {result.get('description', 'Unknown error')}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False


def send_test_message(token: str, chat_id: str, chat_name: str):
    """Envía un mensaje de prueba (solo si se solicita explícitamente)"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    test_message = "🧪 Mensaje de prueba desde diagnóstico"
    
    data = {
        "chat_id": chat_id,
        "text": test_message
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Mensaje de prueba enviado a {chat_name}")
            return True
        else:
            error_desc = result.get('description', 'Unknown error')
            error_code = result.get('error_code', '')
            print(f"❌ Error al enviar mensaje: {error_desc} (código: {error_code})")
            
            if "chat not found" in error_desc.lower():
                print("   💡 El bot no está en el grupo o el Chat ID es incorrecto")
            elif "not enough rights" in error_desc.lower():
                print("   💡 El bot no tiene permisos para enviar mensajes")
            elif "bad request" in error_desc.lower():
                print("   💡 El Chat ID podría estar mal formateado")
            
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Diagnóstico del workflow de GitHub Actions")
    parser.add_argument(
        "--send-test",
        action="store_true",
        help="Enviar mensajes de prueba (por defecto solo verifica configuración)"
    )
    
    args = parser.parse_args()
    
    print("🔧 Diagnóstico del Workflow de GitHub Actions")
    print("=" * 50)
    print()
    
    # Verificar configuración
    if not check_telegram_config():
        print("\n❌ Configuración incompleta")
        sys.exit(1)
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    preview_chat_id = os.getenv("TELEGRAM_PREVIEW_CHAT_ID")
    public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
    
    # Verificar preview chat (sin enviar mensaje por defecto)
    if preview_chat_id:
        preview_chat_id = str(preview_chat_id).strip()
        test_telegram_connection(token, preview_chat_id, "Chat de Revisión (Preview)", send_test=args.send_test)
    
    # Verificar public chat (sin enviar mensaje por defecto)
    if public_chat_id:
        public_chat_id = str(public_chat_id).strip()
        test_telegram_connection(token, public_chat_id, "Grupo Público", send_test=args.send_test)
    
    print("\n" + "=" * 50)
    print("📋 Resumen:")
    print("=" * 50)
    print()
    if args.send_test:
        print("✅ Verificación completa (con mensajes de prueba enviados)")
    else:
        print("✅ Verificación completa (solo configuración, sin enviar mensajes)")
        print("   💡 Para enviar mensajes de prueba, usa: --send-test")
    print()
    print("Si todos los tests pasaron, el problema podría ser:")
    print("1. El informe del día no existe en reports/")
    print("2. El mensaje está vacío o mal formateado")
    print("3. Error en el script send-daily-report-review.py")
    print()
    print("Para ver los logs completos del workflow:")
    print("1. Ve a GitHub → Actions")
    print("2. Click en el último workflow ejecutado")
    print("3. Revisa los logs de cada step")


if __name__ == "__main__":
    main()




