#!/usr/bin/env python3
"""
Prueba la conexión con el webhook server en Render
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

# Obtener URL del webhook (puede estar en .env o usar la default)
webhook_url = os.getenv("WEBHOOK_URL", "https://informessi-webhook.onrender.com")

print("🧪 Prueba de Conexión con Webhook Server")
print("=" * 50)
print()
print(f"🌐 URL del webhook: {webhook_url}")
print()

# Probar endpoint de salud
print("1. Probando endpoint /health...")
try:
    health_url = f"{webhook_url}/health"
    response = requests.get(health_url, timeout=10)
    response.raise_for_status()
    data = response.json()
    print(f"   ✅ Servidor activo: {data.get('status')}")
    print(f"   📅 Timestamp: {data.get('timestamp')}")
except requests.exceptions.Timeout:
    print("   ⏱️  Timeout: El servidor puede estar dormido")
    print("   💡 Render puede tardar 30-60s en 'despertar' el servicio")
except requests.exceptions.RequestException as e:
    print(f"   ❌ Error: {e}")
    print("   💡 Verifica que el servicio esté activo en Render")
except Exception as e:
    print(f"   ❌ Error inesperado: {e}")

print()

# Verificar webhook configurado en Telegram
print("2. Verificando webhook en Telegram...")
token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    print("   ⚠️  TELEGRAM_BOT_TOKEN no configurado")
else:
    try:
        webhook_info_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        response = requests.get(webhook_info_url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            webhook_info = result.get("result", {})
            configured_url = webhook_info.get("url")
            pending_updates = webhook_info.get("pending_update_count", 0)
            
            if configured_url:
                print(f"   ✅ Webhook configurado: {configured_url}")
                if configured_url == f"{webhook_url}/webhook":
                    print("   ✅ URL coincide con el servidor")
                else:
                    print(f"   ⚠️  URL no coincide:")
                    print(f"      Configurado: {configured_url}")
                    print(f"      Esperado: {webhook_url}/webhook")
                    print(f"   💡 Actualiza con:")
                    print(f"      python3 scripts/setup-webhook.py --webhook-url {webhook_url}")
                
                if pending_updates > 0:
                    print(f"   ⚠️  Hay {pending_updates} actualizaciones pendientes")
                    print("   💡 Esto puede indicar que el webhook no está procesando correctamente")
            else:
                print("   ❌ Webhook no configurado")
                print(f"   💡 Configura con:")
                print(f"      python3 scripts/setup-webhook.py --webhook-url {webhook_url}")
        else:
            print(f"   ❌ Error: {result.get('description', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Error al verificar webhook: {e}")

print()
print("=" * 50)
print("📋 Resumen:")
print("=" * 50)
print()
print("Si el servidor está activo pero no recibes callbacks:")
print("1. Verifica que el webhook esté configurado correctamente en Telegram")
print("2. Prueba enviar un mensaje al bot y revisa los logs de Render")
print("3. El servicio puede tardar 30-60s en 'despertar' en Render")
print()
print("Para ver logs en tiempo real:")
print("1. Ve a Render → Tu servicio → Logs")
print("2. Mantén la ventana abierta")
print("3. Click en 'Aprobar' en Telegram")
print("4. Deberías ver logs inmediatamente")






