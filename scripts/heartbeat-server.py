#!/usr/bin/env python3
"""
Servidor simple de heartbeat para InforMessi
Recibe heartbeats de PCs locales y permite verificar disponibilidad
"""
from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, timedelta, time as dt_time
from pathlib import Path

app = Flask(__name__)

# Directorio para almacenar heartbeats
DATA_DIR = Path("/app/data")
HEARTBEAT_FILE = DATA_DIR / "heartbeats.json"
# Hora límite: si no hay heartbeat del día antes de esta hora, PC no está disponible
DEADLINE_HOUR = 10
DEADLINE_MINUTE = 15


def load_heartbeats():
    """Carga heartbeats desde archivo"""
    if not HEARTBEAT_FILE.exists():
        return {}
    
    try:
        with open(HEARTBEAT_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_heartbeats(heartbeats):
    """Guarda heartbeats en archivo"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HEARTBEAT_FILE, 'w') as f:
        json.dump(heartbeats, f, indent=2)


@app.route('/heartbeat', methods=['POST'])
def receive_heartbeat():
    """Recibe heartbeat de PC local"""
    try:
        data = request.json
        pc_id = data.get('pc_id', 'unknown')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        status = data.get('status', 'online')
        
        heartbeats = load_heartbeats()
        # Extraer fecha y hora del timestamp
        heartbeat_dt = datetime.fromisoformat(timestamp)
        
        heartbeats[pc_id] = {
            'timestamp': timestamp,
            'status': status,
            'date': data.get('date', heartbeat_dt.strftime("%Y-%m-%d")),
            'time': data.get('time', heartbeat_dt.strftime("%H:%M:%S")),
            'last_update': datetime.now().isoformat()
        }
        save_heartbeats(heartbeats)
        
        return jsonify({
            'status': 'ok',
            'message': f'Heartbeat recibido de {pc_id}',
            'timestamp': timestamp
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/check/<pc_id>', methods=['GET'])
def check_pc(pc_id):
    """Verifica si una PC está disponible hoy antes de las 10:15 AM"""
    heartbeats = load_heartbeats()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_time = now.time()
    deadline = dt_time(DEADLINE_HOUR, DEADLINE_MINUTE)
    
    # Si ya pasó la hora límite, no verificar heartbeat (VPS debe ejecutar)
    if current_time >= deadline:
        return jsonify({
            'available': False,
            'reason': f'Ya pasó la hora límite ({DEADLINE_HOUR}:{DEADLINE_MINUTE:02d}). Hora actual: {current_time.strftime("%H:%M:%S")}',
            'deadline_passed': True,
            'current_time': current_time.strftime("%H:%M:%S")
        }), 200
    
    # Si no hay heartbeat registrado nunca
    if pc_id not in heartbeats:
        return jsonify({
            'available': False,
            'reason': 'No heartbeat recibido nunca',
            'deadline_passed': False
        }), 200
    
    heartbeat = heartbeats[pc_id]
    heartbeat_date = heartbeat.get('date', '')
    heartbeat_timestamp = datetime.fromisoformat(heartbeat['timestamp'])
    heartbeat_time = heartbeat_timestamp.time()
    
    # Verificar si el heartbeat es del día de hoy
    if heartbeat_date != today:
        return jsonify({
            'available': False,
            'reason': f'No hay heartbeat del día de hoy. Último heartbeat: {heartbeat_date}',
            'last_heartbeat_date': heartbeat_date,
            'today': today,
            'deadline_passed': False
        }), 200
    
    # Verificar que el heartbeat sea antes de la hora límite
    if heartbeat_time >= deadline:
        return jsonify({
            'available': False,
            'reason': f'Heartbeat recibido después de la hora límite ({DEADLINE_HOUR}:{DEADLINE_MINUTE:02d})',
            'heartbeat_time': heartbeat_time.strftime("%H:%M:%S"),
            'deadline_passed': False
        }), 200
    
    # PC está disponible (hay heartbeat del día de hoy antes de la hora límite)
    return jsonify({
        'available': True,
        'last_heartbeat': heartbeat['timestamp'],
        'heartbeat_date': heartbeat_date,
        'heartbeat_time': heartbeat_time.strftime("%H:%M:%S"),
        'deadline_passed': False,
        'current_time': current_time.strftime("%H:%M:%S")
    }), 200


@app.route('/status', methods=['GET'])
def status():
    """Estado del servidor"""
    heartbeats = load_heartbeats()
    return jsonify({
        'status': 'ok',
        'registered_pcs': list(heartbeats.keys()),
        'total_pcs': len(heartbeats)
    }), 200


if __name__ == '__main__':
    print("🚀 Servidor de heartbeat iniciado")
    print(f"   Puerto: 8080")
    print(f"   Archivo de datos: {HEARTBEAT_FILE}")
    app.run(host='0.0.0.0', port=8080, debug=False)

