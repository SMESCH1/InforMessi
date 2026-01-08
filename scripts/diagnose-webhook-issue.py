#!/usr/bin/env python3
"""
Diagnostica problemas con el webhook y los botones de Telegram
MVP - InforMessi
"""

import os
import sys
import requests
from pathlib import Path

# Cargar variables de entorno
def load_env_file(env_path):
    """Carga variables de entorno desde archivo .env manualmente"""
    if not env_path.exists():
        return
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                if key and value and key not in os.environ:
                    os.environ[key] = value

env_path = Path(__file__).parent.parent / ".env"
load_env_file(env_path)

try:
    from dotenv import load_dotenv
    load_dotenv(env_path)
except:
    pass

print("🔍 Diagnóstico de Webhook y Botones")
print("=" * 60)
print()

# 1. Verificar token
token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    print("❌ TELEGRAM_BOT_TOKEN no configurado")
    print("   Configura el token en .env")
    sys.exit(1)

print(f"✅ Token encontrado: {'*' * 20}...{token[-10:]}")
print()

# 2. Verificar que el token sea válido
print("🧪 Verificando token con Telegram API...")
url = f"https://api.telegram.org/bot{token}/getMe"
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    result = response.json()
    
    if result.get("ok"):
        bot_info = result.get("result", {})
        print(f"✅ Token válido")
        print(f"   Bot: @{bot_info.get('username')}")
        print(f"   Nombre: {bot_info.get('first_name')}")
    else:
        print(f"❌ Token inválido: {result.get('description', 'Unknown error')}")
        print("   Obtén un nuevo token de @BotFather")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error al verificar token: {e}")
    sys.exit(1)

print()

# 3. Verificar webhook
print("🔗 Verificando configuración del webhook...")
url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    result = response.json()
    
    if result.get("ok"):
        webhook_info = result.get("result", {})
        webhook_url = webhook_info.get("url", "")
        pending_updates = webhook_info.get("pending_update_count", 0)
        last_error_date = webhook_info.get("last_error_date")
        last_error_message = webhook_info.get("last_error_message")
        
        if webhook_url:
            print(f"✅ Webhook configurado: {webhook_url}")
            print(f"   Updates pendientes: {pending_updates}")
            
            if last_error_date:
                print(f"   ⚠️  Último error: {last_error_message}")
                print(f"   Fecha: {last_error_date}")
            
            # Verificar que el servidor responda
            print()
            print("🌐 Verificando que el servidor webhook responda...")
            try:
                health_url = webhook_url.replace("/webhook", "/health")
                health_response = requests.get(health_url, timeout=5)
                if health_response.status_code == 200:
                    print(f"✅ Servidor webhook está activo")
                else:
                    print(f"⚠️  Servidor responde con código {health_response.status_code}")
            except Exception as e:
                print(f"❌ Servidor webhook no responde: {e}")
                print("   Verifica que Render esté activo y el servicio esté corriendo")
        else:
            print("❌ Webhook no configurado")
            print("   Configura el webhook con:")
            print("   python3 scripts/setup-webhook.py --webhook-url https://tu-webhook.onrender.com")
    else:
        print(f"❌ Error al obtener información del webhook: {result.get('description', 'Unknown error')}")
except Exception as e:
    print(f"❌ Error al verificar webhook: {e}")

print()

# 4. Verificar variables de entorno
print("📋 Verificando variables de entorno...")
preview_chat_id = os.getenv("TELEGRAM_PREVIEW_CHAT_ID")
public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")

if preview_chat_id:
    print(f"✅ TELEGRAM_PREVIEW_CHAT_ID: {preview_chat_id}")
else:
    print("❌ TELEGRAM_PREVIEW_CHAT_ID no configurado")

if public_chat_id:
    print(f"✅ TELEGRAM_PUBLIC_CHAT_ID: {public_chat_id}")
else:
    print("❌ TELEGRAM_PUBLIC_CHAT_ID no configurado")

print()
print("=" * 60)
print("💡 Próximos pasos:")
print()
print("1. Si el token es inválido:")
print("   - Habla con @BotFather en Telegram")
print("   - Usa /token para obtener tu token")
print("   - Actualiza en .env, GitHub Secrets y Render")
print()
print("2. Si el webhook no está configurado:")
print("   python3 scripts/setup-webhook.py --webhook-url https://tu-webhook.onrender.com")
print()
print("3. Si el servidor no responde:")
print("   - Verifica que Render esté activo")
print("   - Revisa los logs de Render")
print("   - Verifica que las variables de entorno estén configuradas en Render")
print()
print("4. Para probar los botones:")
print("   - Ejecuta: python3 scripts/send-daily-report-review.py")
print("   - Haz clic en un botón en Telegram")
print("   - Revisa los logs de Render inmediatamente")
print("=" * 60)




