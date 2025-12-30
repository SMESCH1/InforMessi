#!/usr/bin/env python3
"""
Prueba el flujo de aprobación del webhook
MVP - InforMessi
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime

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

token = os.getenv("TELEGRAM_BOT_TOKEN")
preview_chat_id = os.getenv("TELEGRAM_PREVIEW_CHAT_ID")
public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")

print("🧪 Prueba de Aprobación del Webhook")
print("=" * 50)
print()

if not token:
    print("❌ TELEGRAM_BOT_TOKEN no configurado")
    sys.exit(1)

if not preview_chat_id:
    print("❌ TELEGRAM_PREVIEW_CHAT_ID no configurado")
    sys.exit(1)

if not public_chat_id:
    print("❌ TELEGRAM_PUBLIC_CHAT_ID no configurado")
    print("   Este es necesario para publicar en el grupo público")
    sys.exit(1)

print("✅ Variables configuradas:")
print(f"   Preview Chat ID: {preview_chat_id}")
print(f"   Public Chat ID: {public_chat_id}")
print()

# Verificar webhook configurado
webhook_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
try:
    response = requests.get(webhook_url, timeout=10)
    webhook_data = response.json()
    if webhook_data.get("ok"):
        webhook_info = webhook_data["result"]
        webhook_url_configured = webhook_info.get("url")
        if webhook_url_configured:
            print(f"✅ Webhook configurado: {webhook_url_configured}")
        else:
            print("❌ Webhook no configurado")
            print("   Configura con: python3 scripts/setup-webhook.py --webhook-url TU_URL")
            sys.exit(1)
    else:
        print("❌ Error al obtener información del webhook")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error al verificar webhook: {e}")
    sys.exit(1)

print()
print("📋 Checklist para aprobación:")
print("=" * 50)
print()
print("1. ✅ Webhook configurado")
print("2. ✅ TELEGRAM_PUBLIC_CHAT_ID configurado")
print()
print("💡 Para probar la aprobación:")
print("   1. Envía un mensaje al bot en el chat preview")
print("   2. Click en 'Aprobar'")
print("   3. El webhook debería recibir el callback")
print("   4. Revisa los logs de Render para ver si hay errores")
print()
print("🔍 Si no funciona, verifica:")
print("   - Que el webhook server esté activo en Render")
print("   - Que TELEGRAM_PUBLIC_CHAT_ID esté correcto en Render")
print("   - Que el bot esté en el grupo público")
print("   - Que el bot tenga permisos en el grupo público")
print()
print("📊 Para revisar logs de Render:")
print("   1. Ve a Render → Tu servicio → Logs")
print("   2. Busca errores cuando clickeas 'Aprobar'")



