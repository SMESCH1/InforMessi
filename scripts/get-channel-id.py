#!/usr/bin/env python3
"""
Script para obtener el Chat ID de un canal de Telegram
Útil para configurar TELEGRAM_PUBLIC_CHAT_ID con un canal
"""

import sys
import os
import requests
from pathlib import Path

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def get_channel_id(token: str, channel_username: str = None):
    """Obtiene el Chat ID de un canal"""
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        print("   Configúralo en .env o como variable de entorno")
        return None
    
    # Si se proporciona username, intentar obtener info del canal
    if channel_username:
        if not channel_username.startswith('@'):
            channel_username = f"@{channel_username}"
        
        print(f"🔍 Obteniendo información del canal: {channel_username}")
        print("=" * 60)
        
        # Intentar obtener información del canal
        url = f"https://api.telegram.org/bot{token}/getChat"
        data = {"chat_id": channel_username}
        
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get("ok"):
                chat_info = result.get("result", {})
                chat_id = chat_info.get("id")
                chat_title = chat_info.get("title", "N/A")
                chat_type = chat_info.get("type", "N/A")
                username = chat_info.get("username", "N/A")
                
                print(f"✅ Canal encontrado:")
                print(f"   Nombre: {chat_title}")
                print(f"   Tipo: {chat_type}")
                print(f"   Username: {username}")
                print(f"   Chat ID numérico: {chat_id}")
                print()
                print(f"📋 Para configurar en .env:")
                print(f"   TELEGRAM_PUBLIC_CHAT_ID={channel_username}")
                print(f"   # O usando el ID numérico:")
                print(f"   TELEGRAM_PUBLIC_CHAT_ID={chat_id}")
                print()
                print(f"💡 Recomendación: Usa el username ({channel_username}) si el canal es público")
                print(f"   Es más fácil de mantener y no cambia si recreas el canal")
                
                return chat_id
            else:
                error_desc = result.get('description', 'Unknown error')
                print(f"❌ Error: {error_desc}")
                
                if "chat not found" in error_desc.lower():
                    print()
                    print("💡 Posibles causas:")
                    print("   1. El bot no es administrador del canal")
                    print("   2. El username del canal es incorrecto")
                    print("   3. El canal es privado (necesitas el Chat ID numérico)")
                    print()
                    print("💡 Soluciones:")
                    print("   1. Agrega el bot como administrador del canal")
                    print("   2. Verifica el username (debe ser sin @ en el comando)")
                    print("   3. Para canales privados, usa otro método para obtener el Chat ID")
                
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return None
    
    else:
        print("📋 Métodos para obtener Chat ID de un canal:")
        print("=" * 60)
        print()
        print("Método 1: Usando el username del canal (si es público)")
        print("   python3 scripts/get-channel-id.py @nombre_canal")
        print()
        print("Método 2: Enviar un mensaje al canal y usar getUpdates")
        print("   1. Agrega el bot como administrador del canal")
        print("   2. Publica un mensaje en el canal")
        print("   3. Ejecuta: python3 scripts/get-telegram-chat-id.py")
        print()
        print("Método 3: Usar @userinfobot")
        print("   1. Agrega @userinfobot al canal")
        print("   2. Envía /start en el canal")
        print("   3. @userinfobot te dará el Chat ID")
        print()
        print("Método 4: Desde la URL del canal")
        print("   Si el canal es público: https://t.me/nombre_canal")
        print("   El username es: @nombre_canal")
        print("   Puedes usar directamente: TELEGRAM_PUBLIC_CHAT_ID=@nombre_canal")
        
        return None


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Obtener Chat ID de un canal de Telegram"
    )
    parser.add_argument(
        "channel",
        nargs="?",
        help="Username del canal (con o sin @). Ej: @informessi o informessi"
    )
    
    args = parser.parse_args()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if args.channel:
        get_channel_id(token, args.channel)
    else:
        get_channel_id(token)


if __name__ == "__main__":
    main()

