#!/usr/bin/env python3
"""
Script para encender la instancia EC2 desde la PC local
Úsalo cuando necesites que la VPS esté disponible
"""
import boto3
import os
import sys
import time
from datetime import datetime

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

AWS_INSTANCE_ID = os.getenv("AWS_INSTANCE_ID")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

if not AWS_INSTANCE_ID:
    print("❌ Error: AWS_INSTANCE_ID no configurado en .env")
    print("   Agrega: AWS_INSTANCE_ID=i-1234567890abcdef0")
    sys.exit(1)

def check_instance_status(ec2, instance_id):
    """Verifica el estado de la instancia"""
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        if response['Reservations']:
            instance = response['Reservations'][0]['Instances'][0]
            state = instance['State']['Name']
            ip = instance.get('PublicIpAddress', 'N/A')
            return state, ip
        return None, None
    except Exception as e:
        print(f"❌ Error al verificar estado: {e}")
        return None, None

def start_instance(ec2, instance_id):
    """Enciende la instancia"""
    try:
        print(f"🚀 Encendiendo instancia {instance_id}...")
        ec2.start_instances(InstanceIds=[instance_id])
        
        # Esperar a que esté running
        print("⏳ Esperando a que la instancia esté lista...")
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id], WaiterConfig={'Delay': 10, 'MaxAttempts': 30})
        
        # Obtener IP pública
        state, ip = check_instance_status(ec2, instance_id)
        if state == 'running':
            print(f"✅ Instancia encendida exitosamente")
            print(f"   Estado: {state}")
            print(f"   IP Pública: {ip}")
            return True, ip
        else:
            print(f"⚠️  Instancia en estado: {state}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error al encender instancia: {e}")
        return False, None

def main():
    """Función principal"""
    print("🔌 Encender Instancia EC2 - InforMessi")
    print("=" * 50)
    print(f"Instance ID: {AWS_INSTANCE_ID}")
    print(f"Region: {AWS_REGION}")
    print("")
    
    # Crear cliente EC2
    try:
        ec2 = boto3.client('ec2', region_name=AWS_REGION)
    except Exception as e:
        print(f"❌ Error al conectar con AWS: {e}")
        print("   Verifica tus credenciales AWS:")
        print("   - AWS_ACCESS_KEY_ID")
        print("   - AWS_SECRET_ACCESS_KEY")
        print("   O configura: aws configure")
        sys.exit(1)
    
    # Verificar estado actual
    state, ip = check_instance_status(ec2, AWS_INSTANCE_ID)
    
    if state is None:
        print("❌ No se pudo obtener el estado de la instancia")
        sys.exit(1)
    
    print(f"📊 Estado actual: {state}")
    if ip:
        print(f"   IP Pública: {ip}")
    print("")
    
    if state == 'running':
        print("✅ La instancia ya está encendida")
        print(f"   IP: {ip}")
        sys.exit(0)
    elif state == 'stopped':
        success, new_ip = start_instance(ec2, AWS_INSTANCE_ID)
        if success:
            print("")
            print("🎉 Instancia lista para usar")
            print(f"   Conecta con: ssh -i tu-clave.pem ubuntu@{new_ip}")
            sys.exit(0)
        else:
            sys.exit(1)
    elif state == 'stopping':
        print("⏳ La instancia se está apagando...")
        print("   Espera unos minutos e intenta de nuevo")
        sys.exit(1)
    elif state == 'pending':
        print("⏳ La instancia se está encendiendo...")
        print("   Espera unos minutos")
        sys.exit(1)
    else:
        print(f"⚠️  Estado desconocido: {state}")
        sys.exit(1)

if __name__ == "__main__":
    main()

