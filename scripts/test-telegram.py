#!/usr/bin/env python3
"""
Script de prueba para Telegram
Prueba envío a chat de revisión y grupo público
"""

import os
import sys
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

PROJECT_ROOT = Path(__file__).parent.parent


def test_review_chat(token: str, preview_chat_id: str):
    """Prueba envío al chat de revisión"""
    import requests
    
    print("🧪 Probando chat de revisión (privado)...")
    
    test_message = """🧪 <b>PRUEBA - Chat de Revisión</b>

Este es un mensaje de prueba para verificar que el bot puede enviar al chat de revisión.

Si ves este mensaje con botones, el chat de revisión está configurado correctamente.

✅ Aprobar
❌ Rechazar
✏️ Editar"""
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": preview_chat_id,
        "text": test_message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        print("✅ Mensaje enviado al chat de revisión")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_public_chat(token: str, public_chat_id: str):
    """Prueba envío al grupo público"""
    import requests
    
    print("\n🧪 Probando grupo público...")
    
    test_message = """🧪 <b>PRUEBA - Grupo Público</b>

Este es un mensaje de prueba para verificar que el bot puede enviar al grupo público.

Si ves este mensaje, el grupo público está configurado correctamente."""
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": public_chat_id,
        "text": test_message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        print("✅ Mensaje enviado al grupo público")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_with_photo(token: str, chat_id: str, is_public: bool = False):
    """Prueba envío de foto"""
    import requests
    from pathlib import Path
    
    print(f"\n🧪 Probando envío de foto ({'grupo público' if is_public else 'chat de revisión'})...")
    
    # Buscar una imagen de prueba en assets/media
    media_dir = PROJECT_ROOT / "assets" / "media"
    test_image = None
    
    if media_dir.exists():
        for date_dir in sorted(media_dir.iterdir(), reverse=True):
            if date_dir.is_dir():
                for img_file in date_dir.glob("*.jpg"):
                    test_image = img_file
                    break
                if test_image:
                    break
                for img_file in date_dir.glob("*.png"):
                    test_image = img_file
                    break
                if test_image:
                    break
    
    if not test_image:
        print("⚠️  No se encontró imagen de prueba en assets/media/")
        print("   Creando imagen de prueba dummy...")
        # Crear imagen dummy pequeña
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='blue')
        test_image = PROJECT_ROOT / "tmp" / "test-image.jpg"
        test_image.parent.mkdir(exist_ok=True)
        img.save(test_image)
        print(f"   Imagen de prueba creada: {test_image}")
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    try:
        with open(test_image, 'rb') as photo:
            files = {'photo': photo}
            data = {
                "chat_id": chat_id,
                "caption": "🧪 <b>PRUEBA - Foto</b>\n\nSi ves esta foto, el envío de imágenes funciona correctamente.",
                "parse_mode": "HTML"
            }
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            print(f"✅ Foto enviada correctamente")
            return True
    except ImportError:
        print("⚠️  PIL no instalado, saltando prueba de foto")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Prueba la configuración de Telegram"
    )
    parser.add_argument(
        "--review-only",
        action="store_true",
        help="Solo probar chat de revisión"
    )
    parser.add_argument(
        "--public-only",
        action="store_true",
        help="Solo probar grupo público"
    )
    parser.add_argument(
        "--with-photo",
        action="store_true",
        help="Incluir prueba de envío de foto"
    )
    
    args = parser.parse_args()
    
    # Cargar variables de entorno
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    preview_chat_id = os.getenv("TELEGRAM_PREVIEW_CHAT_ID")
    public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        sys.exit(1)
    
    print("🧪 Pruebas de Telegram - InforMessi")
    print("=" * 50)
    print("")
    
    results = {}
    
    # Probar chat de revisión
    if not args.public_only:
        if not preview_chat_id:
            print("⚠️  TELEGRAM_PREVIEW_CHAT_ID no configurado")
            print("   Saltando prueba de chat de revisión")
        else:
            results['review'] = test_review_chat(token, preview_chat_id)
            if args.with_photo:
                test_with_photo(token, preview_chat_id, is_public=False)
    
    # Probar grupo público
    if not args.review_only:
        if not public_chat_id:
            print("\n⚠️  TELEGRAM_PUBLIC_CHAT_ID no configurado")
            print("   Saltando prueba de grupo público")
        else:
            results['public'] = test_public_chat(token, public_chat_id)
            if args.with_photo:
                test_with_photo(token, public_chat_id, is_public=True)
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 Resumen de Pruebas:")
    print("=" * 50)
    
    if 'review' in results:
        status = "✅ OK" if results['review'] else "❌ FALLO"
        print(f"   Chat de revisión: {status}")
    
    if 'public' in results:
        status = "✅ OK" if results['public'] else "❌ FALLO"
        print(f"   Grupo público: {status}")
    
    if not results:
        print("   ⚠️  No se ejecutaron pruebas (configuración incompleta)")


if __name__ == "__main__":
    main()

