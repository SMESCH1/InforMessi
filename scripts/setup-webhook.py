#!/usr/bin/env python3
"""
Configura el webhook de Telegram para el servidor webhook
MVP - InforMessi
"""

import os
import sys
import requests
from pathlib import Path

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

def setup_webhook(token: str, webhook_url: str):
    """Configura el webhook en Telegram"""
    
    url = f"https://api.telegram.org/bot{token}/setWebhook"
    data = {"url": f"{webhook_url}/webhook"}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            print("✅ Webhook configurado exitosamente")
            print(f"   URL: {webhook_url}/webhook")
            return True
        else:
            print(f"❌ Error: {result.get('description', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Error al configurar webhook: {e}")
        return False


def get_webhook_info(token: str):
    """Obtiene información del webhook actual"""
    
    url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            info = result.get("result", {})
            print("\n📋 Información del Webhook:")
            print(f"   URL: {info.get('url', 'No configurado')}")
            print(f"   Pending updates: {info.get('pending_update_count', 0)}")
            if info.get('last_error_date'):
                print(f"   ⚠️  Último error: {info.get('last_error_message')}")
            return info
        else:
            print(f"❌ Error: {result.get('description', 'Unknown error')}")
            return None
    
    except Exception as e:
        print(f"❌ Error al obtener información: {e}")
        return None


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Configura el webhook de Telegram"
    )
    parser.add_argument(
        "--webhook-url",
        help="URL del servidor webhook (ej: https://tu-proyecto.up.railway.app)"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Solo muestra información del webhook actual"
    )
    
    args = parser.parse_args()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
        sys.exit(1)
    
    if args.info:
        get_webhook_info(token)
        return
    
    webhook_url = args.webhook_url or os.getenv("WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ WEBHOOK_URL no especificado")
        print("   Usa: --webhook-url https://tu-servidor.com")
        print("   O configura WEBHOOK_URL en .env")
        sys.exit(1)
    
    # Asegurar que la URL no termine en /
    webhook_url = webhook_url.rstrip('/')
    
    print("🔧 Configurando webhook de Telegram...")
    print(f"   Bot Token: {token[:10]}...")
    print(f"   Webhook URL: {webhook_url}/webhook")
    print()
    
    if setup_webhook(token, webhook_url):
        print()
        get_webhook_info(token)


if __name__ == "__main__":
    main()

