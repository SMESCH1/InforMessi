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


def test_telegram_connection(token: str, chat_id: str, chat_name: str):
    """Prueba conexión con Telegram"""
    print(f"\n🧪 Probando conexión con {chat_name}...")
    print("-" * 50)
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Mensaje de prueba
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
            print(f"✅ Mensaje enviado exitosamente a {chat_name}")
            print(f"   Message ID: {result.get('result', {}).get('message_id')}")
            return True
        else:
            error_desc = result.get('description', 'Unknown error')
            error_code = result.get('error_code', '')
            print(f"❌ Error de Telegram: {error_desc} (código: {error_code})")
            
            # Diagnóstico específico
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
    
    # Probar preview chat
    if preview_chat_id:
        preview_chat_id = str(preview_chat_id).strip()
        test_telegram_connection(token, preview_chat_id, "Chat de Revisión (Preview)")
    
    # Probar public chat
    if public_chat_id:
        public_chat_id = str(public_chat_id).strip()
        test_telegram_connection(token, public_chat_id, "Grupo Público")
    
    print("\n" + "=" * 50)
    print("📋 Resumen:")
    print("=" * 50)
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

