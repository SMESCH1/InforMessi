#!/usr/bin/env python3
"""
Verifica si la PC local está disponible antes de ejecutar en VPS
Verifica si hay un heartbeat del día actual antes de las 10:15 AM
"""
import requests
import os
import sys
from datetime import datetime, time as dt_time

VPS_HEARTBEAT_URL = os.getenv("VPS_HEARTBEAT_URL", "http://localhost:8080")
PC_ID = os.getenv("PC_ID", "pc-sebastian")
DEADLINE_HOUR = 10
DEADLINE_MINUTE = 15


def check_pc_available():
    """Verifica si la PC local está disponible (tiene heartbeat del día antes de 10:15 AM)"""
    try:
        url = f"{VPS_HEARTBEAT_URL}/check/{PC_ID}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('available', False), data
        else:
            print(f"⚠️  Error al verificar PC: {response.status_code}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ No se puede conectar al servidor de heartbeat: {VPS_HEARTBEAT_URL}")
        print(f"   Asumiendo que PC no está disponible")
        return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None


if __name__ == "__main__":
    now = datetime.now()
    current_time = now.time()
    deadline = dt_time(DEADLINE_HOUR, DEADLINE_MINUTE)
    
    print(f"🔍 Verificando disponibilidad de PC local ({PC_ID})")
    print(f"   Hora actual: {current_time.strftime('%H:%M:%S')}")
    print(f"   Hora límite: {deadline.strftime('%H:%M:%S')}")
    print("")
    
    available, data = check_pc_available()
    
    if available:
        print(f"✅ PC local ({PC_ID}) está disponible")
        print(f"   Heartbeat del día: {data.get('heartbeat_date', 'N/A')}")
        print(f"   Hora del heartbeat: {data.get('heartbeat_time', 'N/A')}")
        print(f"   Hora actual: {data.get('current_time', 'N/A')}")
        print("")
        print("   → No ejecutar en VPS (PC local lo hará)")
        sys.exit(0)  # PC disponible, no ejecutar en VPS
    else:
        print(f"⚠️  PC local ({PC_ID}) NO está disponible")
        if data:
            print(f"   Razón: {data.get('reason', 'N/A')}")
            if data.get('deadline_passed'):
                print(f"   → Ya pasó la hora límite, VPS debe ejecutar")
            else:
                print(f"   → No hay heartbeat del día antes de las {DEADLINE_HOUR}:{DEADLINE_MINUTE:02d}")
        print("")
        print("   → Ejecutar en VPS (fallback)")
        sys.exit(1)  # PC no disponible, ejecutar en VPS

