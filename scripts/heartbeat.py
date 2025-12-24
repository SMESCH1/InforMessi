#!/usr/bin/env python3
"""
Heartbeat para InforMessi
Envía señal de que la PC está disponible temprano en la mañana
Se asume que la PC estará encendida, y solo se envía un heartbeat diario
antes de las 10:15 AM para indicar disponibilidad
"""
import requests
import os
from datetime import datetime, time as dt_time

# Configuración
VPS_HEARTBEAT_URL = os.getenv("VPS_HEARTBEAT_URL", "http://localhost:8080/heartbeat")
PC_ID = os.getenv("PC_ID", "pc-sebastian")

# Hora límite: si no hay heartbeat antes de esta hora, VPS asume PC no disponible
DEADLINE_HOUR = 10
DEADLINE_MINUTE = 15


def send_heartbeat():
    """Envía heartbeat al servidor VPS indicando que la PC está disponible"""
    try:
        now = datetime.now()
        current_time = now.time()
        deadline = dt_time(DEADLINE_HOUR, DEADLINE_MINUTE)
        
        # Verificar que sea antes de la hora límite
        if current_time >= deadline:
            print(f"⚠️  Ya pasó la hora límite ({DEADLINE_HOUR}:{DEADLINE_MINUTE:02d})")
            print(f"   Hora actual: {current_time.strftime('%H:%M:%S')}")
            print(f"   El heartbeat debe enviarse antes de las {DEADLINE_HOUR}:{DEADLINE_MINUTE:02d}")
            return False
        
        response = requests.post(
            VPS_HEARTBEAT_URL,
            json={
                "pc_id": PC_ID,
                "timestamp": now.isoformat(),
                "status": "online",
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S")
            },
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Heartbeat enviado exitosamente")
            print(f"   Fecha: {now.strftime('%Y-%m-%d')}")
            print(f"   Hora: {now.strftime('%H:%M:%S')}")
            print(f"   PC ID: {PC_ID}")
            return True
        else:
            print(f"⚠️  Heartbeat falló: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ No se puede conectar al servidor de heartbeat: {VPS_HEARTBEAT_URL}")
        print(f"   Verifica que el servidor esté corriendo y la URL sea correcta")
        return False
    except Exception as e:
        print(f"❌ Error enviando heartbeat: {e}")
        return False


def main():
    """Función principal - envía heartbeat una vez"""
    print(f"🚀 Enviando heartbeat diario de InforMessi")
    print(f"   PC ID: {PC_ID}")
    print(f"   Servidor: {VPS_HEARTBEAT_URL}")
    print(f"   Hora límite: {DEADLINE_HOUR}:{DEADLINE_MINUTE:02d}")
    print("")
    
    success = send_heartbeat()
    
    if success:
        print("")
        print("✅ Heartbeat enviado. La PC está marcada como disponible para hoy.")
        print("   El VPS verificará este heartbeat antes de ejecutar.")
    else:
        print("")
        print("❌ No se pudo enviar el heartbeat.")
        print("   El VPS ejecutará InforMessi si no encuentra heartbeat antes de las 10:15 AM.")
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()

