#!/usr/bin/env python3
"""
Método alternativo para obtener Chat ID cuando hay webhook activo
Envía un mensaje de prueba y revisa los logs de Render
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

token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    print("❌ TELEGRAM_BOT_TOKEN no configurado")
    sys.exit(1)

print("📱 Método Alternativo para Obtener Chat ID")
print("=" * 50)
print()
print("Cuando hay un webhook activo, Telegram no permite usar getUpdates.")
print("Usa este método alternativo:")
print()
print("1. Envía un mensaje en el chat/grupo donde quieres obtener el ID")
print("2. El webhook recibirá el mensaje")
print("3. Revisa los logs de Render para ver el chat_id")
print()
print("O usa este método manual:")
print()
print("1. Abre Telegram")
print("2. Ve al chat/grupo")
print("3. Agrega este bot: @userinfobot")
print("4. El bot te mostrará el Chat ID")
print()
print("5. O usa este método programático:")
print("   - Envía un mensaje al bot en el chat/grupo")
print("   - El webhook lo recibirá")
print("   - Revisa los logs en Render → Tu servicio → Logs")
print("   - Busca 'chat_id' en los logs")
print()
print("💡 Para eliminar temporalmente el webhook:")
print("   python3 scripts/setup-webhook.py --remove")
print()
print("💡 Para restaurar el webhook después:")
print("   python3 scripts/setup-webhook.py --webhook-url https://informessi-webhook.onrender.com")

