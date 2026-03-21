#!/usr/bin/env python3
"""
Script auxiliar para obtener Chat IDs de Telegram
Útil para configurar el sistema de revisión humana
"""

import sys
import os
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

try:
    import requests
except ImportError:
    print("ERROR: Necesitas instalar 'requests': pip install requests")
    sys.exit(1)


def get_chat_id(token: str):
    """Obtiene el chat ID del último mensaje recibido"""
    # Primero verificar si hay webhook configurado
    webhook_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    try:
        webhook_response = requests.get(webhook_url, timeout=10)
        webhook_data = webhook_response.json()
        if webhook_data.get("ok") and webhook_data.get("result", {}).get("url"):
            webhook_info = webhook_data["result"]
            print("⚠️  Webhook detectado (esto causa el error 409)")
            print(f"   URL: {webhook_info.get('url')}")
            print()
            print("💡 Soluciones:")
            print()
            print("Opción 1: Eliminar webhook temporalmente")
            print("   python3 scripts/setup-webhook.py --remove")
            print("   python3 scripts/get-telegram-chat-id.py")
            print("   python3 scripts/setup-webhook.py --webhook-url https://informessi-webhook.onrender.com")
            print()
            print("Opción 2: Usar @userinfobot en Telegram")
            print("   - Agrega @userinfobot al grupo/canal")
            print("   - El bot te mostrará el Chat ID")
            print()
            print("Opción 3: Revisar logs de Render")
            print("   - Envía un mensaje al bot en el grupo")
            print("   - Ve a Render → Tu servicio → Logs")
            print("   - Busca 'chat_id' en los logs del webhook")
            return None
    except:
        pass  # Si falla, continuar con getUpdates
    
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("ok"):
            error_desc = data.get('description', 'Unknown error')
            print(f"❌ Error: {error_desc}")
            
            # Si es error 409, explicar mejor
            if "409" in str(response.status_code) or "conflict" in error_desc.lower():
                print()
                print("💡 Este error ocurre porque hay un webhook activo.")
                print("   Telegram no permite usar getUpdates cuando hay webhook.")
                print()
                print("   Soluciones:")
                print("   1. Elimina el webhook temporalmente:")
                print("      python3 scripts/setup-webhook.py --remove")
                print("   2. O usa @userinfobot en Telegram para obtener el Chat ID")
            return None
        
        updates = data.get("result", [])
        
        if not updates:
            print("⚠️  No hay actualizaciones. Envía un mensaje al bot primero.")
            return None
        
        print("📋 Chat IDs encontrados:\n")
        
        seen_chats = set()
        for update in updates:
            if "message" in update:
                chat = update["message"]["chat"]
                chat_id = chat["id"]
                chat_type = chat["type"]
                chat_title = chat.get("title") or chat.get("first_name", "N/A")
                
                if chat_id not in seen_chats:
                    seen_chats.add(chat_id)
                    print(f"  {chat_type.upper()}: {chat_title}")
                    print(f"    Chat ID: {chat_id}")
                    print()
            
            elif "channel_post" in update:
                chat = update["channel_post"]["chat"]
                chat_id = chat["id"]
                chat_title = chat.get("title", "N/A")
                
                if chat_id not in seen_chats:
                    seen_chats.add(chat_id)
                    print(f"  CHANNEL: {chat_title}")
                    print(f"    Chat ID: {chat_id}")
                    print()
        
        if seen_chats:
            print("💡 Tip: Usa el Chat ID negativo para grupos/canales")
            print("   Agrega estos valores a tu .env:")
            for chat_id in seen_chats:
                print(f"   TELEGRAM_PREVIEW_CHAT_ID={chat_id}")
        
        return list(seen_chats)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al conectar con Telegram: {e}")
        return None


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Obtiene Chat IDs de Telegram para configurar el bot"
    )
    parser.add_argument(
        "--token",
        help="Token del bot (o usa TELEGRAM_BOT_TOKEN)"
    )
    
    args = parser.parse_args()
    
    token = args.token or os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("ERROR: Token de Telegram no encontrado")
        print("   Usa --token o configura TELEGRAM_BOT_TOKEN")
        print("\n   Para obtener el token:")
        print("   1. Habla con @BotFather en Telegram")
        print("   2. Crea un bot con /newbot")
        print("   3. Copia el token que te da")
        sys.exit(1)
    
    print("🔍 Obteniendo Chat IDs de Telegram...")
    print("=" * 50)
    print("\n💡 Instrucciones:")
    print("   1. Asegúrate de que el bot esté agregado al grupo/canal")
    print("   2. Envía un mensaje al grupo/canal")
    print("   3. Ejecuta este script\n")
    
    get_chat_id(token)


if __name__ == "__main__":
    main()

