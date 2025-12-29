#!/usr/bin/env python3
"""
Obtiene Chat ID desde la URL del grupo en Telegram Desktop/Web
Método alternativo cuando los bots no funcionan
MVP - InforMessi
"""

import re
import sys


def extract_chat_id_from_url(url: str) -> str:
    """Extrae el Chat ID de una URL de Telegram"""
    # Patrones comunes de URLs de Telegram
    patterns = [
        r't\.me/c/(\d+)',  # t.me/c/1234567890
        r't\.me/joinchat/([A-Za-z0-9_-]+)',  # t.me/joinchat/ABC123
        r'chat_id=(-?\d+)',  # chat_id=-1001234567890
        r'c/(\d+)',  # c/1234567890
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def main():
    """Función principal"""
    print("📱 Obtener Chat ID desde URL de Telegram")
    print("=" * 50)
    print()
    print("💡 Método alternativo cuando los bots no funcionan:")
    print()
    print("1. Abre Telegram Desktop o Web")
    print("2. Ve al grupo/canal")
    print("3. Click derecho en el grupo → 'Copy link' o 'Copiar enlace'")
    print("4. O desde el navegador, copia la URL completa")
    print("5. Pega la URL aquí")
    print()
    print("Ejemplos de URLs:")
    print("  - https://t.me/c/1234567890")
    print("  - https://web.telegram.org/k/#-1001234567890")
    print()
    
    url = input("Pega la URL aquí: ").strip()
    
    if not url:
        print("❌ URL vacía")
        sys.exit(1)
    
    chat_id = extract_chat_id_from_url(url)
    
    if chat_id:
        print()
        print("✅ Chat ID encontrado:")
        print(f"   {chat_id}")
        print()
        print("💡 Nota: Si el ID es positivo, puede que necesites el negativo.")
        print("   Para grupos, el Chat ID suele ser negativo (ej: -1001234567890)")
        print()
        print("Para actualizar:")
        print(f"   python3 scripts/update-chat-ids.py --public-chat-id {chat_id}")
    else:
        print()
        print("❌ No se pudo extraer Chat ID de la URL")
        print()
        print("💡 Método manual:")
        print("1. Abre Telegram Desktop")
        print("2. Ve al grupo")
        print("3. Click derecho → 'Copy link'")
        print("4. O desde el navegador, copia la URL completa")
        print("5. La URL debería contener el Chat ID")
        print()
        print("Si la URL no contiene el ID, usa este método:")
        print("1. Elimina el webhook temporalmente:")
        print("   python3 scripts/setup-webhook.py --remove")
        print("2. Envía un mensaje al bot en el grupo")
        print("3. Revisa los logs de Render para ver el chat_id")


if __name__ == "__main__":
    main()

