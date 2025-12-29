#!/usr/bin/env python3
"""
Actualiza los Chat IDs de Telegram en todos los lugares necesarios
MVP - InforMessi
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_env_file():
    """Carga variables de entorno desde .env"""
    def load_manual(env_path):
        if not env_path.exists():
            return {}
        env_vars = {}
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
                    env_vars[key] = value
        return env_vars
    
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_FILE)
    except:
        pass
    
    # Cargar manualmente también
    manual_vars = load_manual(ENV_FILE)
    for key, value in manual_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    return manual_vars


def update_env_file(preview_chat_id: str = None, public_chat_id: str = None):
    """Actualiza el archivo .env con los nuevos Chat IDs"""
    if not ENV_FILE.exists():
        print(f"❌ Archivo .env no encontrado en {ENV_FILE}")
        return False
    
    # Leer archivo actual
    lines = []
    preview_updated = False
    public_updated = False
    
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            original_line = line
            line_stripped = line.strip()
            
            # Actualizar TELEGRAM_PREVIEW_CHAT_ID
            if preview_chat_id and line_stripped.startswith('TELEGRAM_PREVIEW_CHAT_ID='):
                lines.append(f'TELEGRAM_PREVIEW_CHAT_ID={preview_chat_id}\n')
                preview_updated = True
                continue
            
            # Actualizar TELEGRAM_PUBLIC_CHAT_ID
            if public_chat_id and line_stripped.startswith('TELEGRAM_PUBLIC_CHAT_ID='):
                lines.append(f'TELEGRAM_PUBLIC_CHAT_ID={public_chat_id}\n')
                public_updated = True
                continue
            
            lines.append(original_line)
    
    # Si no se encontraron, agregarlos al final
    if preview_chat_id and not preview_updated:
        lines.append(f'\nTELEGRAM_PREVIEW_CHAT_ID={preview_chat_id}\n')
    
    if public_chat_id and not public_updated:
        lines.append(f'TELEGRAM_PUBLIC_CHAT_ID={public_chat_id}\n')
    
    # Guardar
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True


def show_update_instructions(preview_chat_id: str = None, public_chat_id: str = None):
    """Muestra instrucciones para actualizar Chat IDs en otros lugares"""
    print("\n📋 Instrucciones para actualizar Chat IDs:")
    print("=" * 50)
    
    if preview_chat_id:
        print(f"\n1. TELEGRAM_PREVIEW_CHAT_ID (Chat Privado):")
        print(f"   Nuevo ID: {preview_chat_id}")
        print(f"   Actualizar en:")
        print(f"   ✅ .env local (ya actualizado)")
        print(f"   ⬜ GitHub Secrets:")
        print(f"      - Ve a tu repo → Settings → Secrets → Actions")
        print(f"      - Edita TELEGRAM_PREVIEW_CHAT_ID")
        print(f"      - Valor: {preview_chat_id}")
    
    if public_chat_id:
        print(f"\n2. TELEGRAM_PUBLIC_CHAT_ID (Grupo Público):")
        print(f"   Nuevo ID: {public_chat_id}")
        print(f"   Actualizar en:")
        print(f"   ✅ .env local (ya actualizado)")
        print(f"   ⬜ GitHub Secrets:")
        print(f"      - Ve a tu repo → Settings → Secrets → Actions")
        print(f"      - Edita TELEGRAM_PUBLIC_CHAT_ID")
        print(f"      - Valor: {public_chat_id}")
        print(f"   ⬜ Render (Variables de Entorno):")
        print(f"      - Ve a Render → Tu servicio → Environment")
        print(f"      - Edita TELEGRAM_PUBLIC_CHAT_ID")
        print(f"      - Valor: {public_chat_id}")
        print(f"      - Guarda cambios (Render reiniciará automáticamente)")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Actualiza Chat IDs de Telegram en .env y muestra instrucciones"
    )
    parser.add_argument(
        "--preview-chat-id",
        help="Nuevo Chat ID del chat privado (revisión)"
    )
    parser.add_argument(
        "--public-chat-id",
        help="Nuevo Chat ID del grupo público"
    )
    parser.add_argument(
        "--show-current",
        action="store_true",
        help="Mostrar Chat IDs actuales"
    )
    
    args = parser.parse_args()
    
    # Cargar variables actuales
    env_vars = load_env_file()
    current_preview = env_vars.get('TELEGRAM_PREVIEW_CHAT_ID') or os.getenv('TELEGRAM_PREVIEW_CHAT_ID')
    current_public = env_vars.get('TELEGRAM_PUBLIC_CHAT_ID') or os.getenv('TELEGRAM_PUBLIC_CHAT_ID')
    
    if args.show_current:
        print("📋 Chat IDs Actuales:")
        print("=" * 50)
        print(f"TELEGRAM_PREVIEW_CHAT_ID: {current_preview or 'No configurado'}")
        print(f"TELEGRAM_PUBLIC_CHAT_ID: {current_public or 'No configurado'}")
        return
    
    if not args.preview_chat_id and not args.public_chat_id:
        print("❌ Debes especificar al menos un Chat ID")
        print("\nUso:")
        print("  python3 scripts/update-chat-ids.py --preview-chat-id 123456789")
        print("  python3 scripts/update-chat-ids.py --public-chat-id -1001234567890")
        print("  python3 scripts/update-chat-ids.py --preview-chat-id 123 --public-chat-id -100456")
        print("\nPara ver los actuales:")
        print("  python3 scripts/update-chat-ids.py --show-current")
        sys.exit(1)
    
    print("🔄 Actualizando Chat IDs...")
    print("=" * 50)
    
    # Actualizar .env
    if args.preview_chat_id or args.public_chat_id:
        update_env_file(
            preview_chat_id=args.preview_chat_id,
            public_chat_id=args.public_chat_id
        )
        print("✅ Archivo .env actualizado")
    
    # Mostrar instrucciones
    show_update_instructions(
        preview_chat_id=args.preview_chat_id,
        public_chat_id=args.public_chat_id
    )


if __name__ == "__main__":
    main()

