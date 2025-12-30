#!/usr/bin/env python3
"""
Verifica que el token del bot sea válido
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

token = os.getenv("TELEGRAM_BOT_TOKEN")

print("🔍 Verificación de Token del Bot")
print("=" * 50)
print()

if not token:
    print("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
    print()
    print("💡 Para obtener un token:")
    print("   1. Abre Telegram")
    print("   2. Habla con @BotFather")
    print("   3. Usa /token para ver tu token actual")
    print("   4. O crea un nuevo bot con /newbot")
    print("   5. Copia el token y agrégalo a .env:")
    print("      TELEGRAM_BOT_TOKEN=tu_token_aqui")
    sys.exit(1)

print(f"📋 Token encontrado: {'*' * 20}...{token[-10:]}")
print()

# Verificar token con getMe
print("🧪 Verificando token con Telegram API...")
url = f"https://api.telegram.org/bot{token}/getMe"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    result = response.json()
    
    if result.get("ok"):
        bot_info = result.get("result", {})
        print("✅ Token válido")
        print(f"   Bot: @{bot_info.get('username')}")
        print(f"   Nombre: {bot_info.get('first_name')}")
        print(f"   ID: {bot_info.get('id')}")
    else:
        error_desc = result.get('description', 'Unknown error')
        print(f"❌ Token inválido: {error_desc}")
        print()
        print("💡 El token puede haber expirado o ser incorrecto")
        print("   Obtén un nuevo token de @BotFather en Telegram")
        sys.exit(1)
        
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("❌ Token inválido o no autorizado (401)")
        print()
        print("💡 Posibles causas:")
        print("   - El token ha expirado")
        print("   - El token es incorrecto")
        print("   - El bot fue eliminado")
        print()
        print("💡 Solución:")
        print("   1. Habla con @BotFather en Telegram")
        print("   2. Usa /token para ver tu token actual")
        print("   3. O crea un nuevo bot con /newbot")
        print("   4. Actualiza TELEGRAM_BOT_TOKEN en .env")
    else:
        print(f"❌ Error HTTP {e.response.status_code}: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print()
print("=" * 50)
print("✅ Token verificado correctamente")
print("=" * 50)



