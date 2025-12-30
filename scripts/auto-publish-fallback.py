#!/usr/bin/env python3
"""
Publicación automática de respaldo
Si no hay aprobación después de X horas, publica automáticamente
MVP - InforMessi
"""

import json
import os
import sys
from datetime import datetime, timedelta
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
    if env_path.exists():
        load_dotenv(env_path, override=True)
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

# Importar funciones de telegram
import requests


def load_report(date: str) -> dict:
    """Carga un informe desde reports/"""
    report_file = REPORTS_DIR / f"{date}.json"
    
    if not report_file.exists():
        return None
    
    with open(report_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def should_auto_publish(report: dict, hours_threshold: float = 2) -> bool:
    """
    Determina si se debe publicar automáticamente
    
    Args:
        report: Diccionario del informe
        hours_threshold: Horas de espera antes de publicar automáticamente
    
    Returns:
        True si debe publicarse, False si no
    """
    # Si ya está publicado, no hacer nada
    if report.get("status") == "published":
        return False
    
    # Si no tiene updated_at, no publicar (informe muy viejo)
    if not report.get("updated_at"):
        return False
    
    # Calcular tiempo desde última actualización
    updated_at = datetime.fromisoformat(report["updated_at"])
    now = datetime.now()
    hours_passed = (now - updated_at).total_seconds() / 3600
    
    # Si pasaron más de X horas, publicar automáticamente
    return hours_passed >= hours_threshold


def auto_publish_report(date: str, hours_threshold: float = 2):
    """Publica un informe automáticamente si no fue aprobado"""
    
    report = load_report(date)
    if not report:
        print(f"❌ Informe para {date} no encontrado")
        return False
    
    # Verificar si debe publicarse
    if not should_auto_publish(report, hours_threshold):
        print(f"ℹ️  Informe para {date} no necesita publicación automática aún")
        return False
    
    # Verificar que tenga mensaje
    message = report.get("message")
    if not message:
        print(f"❌ Informe para {date} no tiene mensaje")
        return False
    
    # Obtener variables de entorno
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
    
    if not token or not public_chat_id:
        print("❌ Variables de Telegram no configuradas")
        print("   Configura TELEGRAM_BOT_TOKEN y TELEGRAM_PUBLIC_CHAT_ID")
        return False
    
    # Publicar
    try:
        # Enviar mensaje directamente usando requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": public_chat_id,
            "text": message
        }
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        
        # Actualizar estado del informe
        report["status"] = "published"
        report["published_at"] = datetime.now().isoformat()
        report["auto_published"] = True  # Marcar como publicación automática
        
        # Guardar
        report_file = REPORTS_DIR / f"{date}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Actualizar base de datos de memoria
        try:
            from update_memory_db import update_memory_for_report
            update_memory_for_report(date)
        except:
            pass  # No crítico si falla
        
        print(f"✅ Informe para {date} publicado automáticamente (fallback)")
        return True
    
    except Exception as e:
        print(f"❌ Error al publicar: {e}")
        return False


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Publica automáticamente informes no aprobados después de X horas"
    )
    parser.add_argument(
        "--date",
        help="Fecha a verificar (YYYY-MM-DD). Default: hoy"
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=2,
        help="Horas de espera antes de publicar automáticamente (default: 2)"
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="Verificar todos los informes de los últimos 7 días"
    )
    
    args = parser.parse_args()
    
    if args.check_all:
        # Verificar últimos 7 días
        today = datetime.now()
        published_count = 0
        
        for i in range(7):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if auto_publish_report(date, args.hours):
                published_count += 1
        
        print(f"\n✅ Proceso completado: {published_count} informe(s) publicados automáticamente")
    else:
        # Verificar fecha específica o hoy
        if args.date:
            target_date = args.date
        else:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        auto_publish_report(target_date, args.hours)


if __name__ == "__main__":
    main()

