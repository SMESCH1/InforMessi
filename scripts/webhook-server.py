#!/usr/bin/env python3
"""
Servidor webhook simple para ejecutar el flujo de InforMessi
Útil para n8n cuando no tiene acceso directo a executeCommand
"""

import os
import sys
import subprocess
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PROJECT_ROOT = "/home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi"


class InforMessiHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Maneja requests POST para ejecutar el flujo"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            command = data.get('command', '')
            
            if not command:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'No command provided'
                }).encode())
                return
            
            # Ejecutar comando
            result = subprocess.run(
                command,
                shell=True,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())
    
    def do_GET(self):
        """Health check"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'ok',
            'service': 'InforMessi Webhook'
        }).encode())
    
    def log_message(self, format, *args):
        """Suprime logs del servidor"""
        pass


def main():
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('localhost', port), InforMessiHandler)
    print(f"🚀 Servidor webhook iniciado en http://localhost:{port}")
    print("   POST /execute - Ejecuta comando")
    print("   GET / - Health check")
    print("\n💡 Para detener: Ctrl+C")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor...")
        server.shutdown()


if __name__ == '__main__':
    main()

