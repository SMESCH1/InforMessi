# Solución: Usar Webhook para n8n

## Problema

El nodo "Code" de n8n no permite usar `child_process` por razones de seguridad.

## Solución: Servidor Webhook

Usaremos un servidor webhook local que ejecuta el script cuando n8n lo llama.

---

## 🚀 Configuración Rápida

### Paso 1: Iniciar Servidor Webhook

Abre una terminal y ejecuta:

```bash
cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi
bash scripts/start-webhook.sh
```

El servidor quedará corriendo y escuchando en `http://localhost:8000`.

**Importante**: Deja esta terminal abierta mientras uses n8n.

### Paso 2: Importar Workflow HTTP

1. En n8n, ve a **"Workflows"** → **"Import from File"**
2. Selecciona: `n8n/workflows/daily-informessi-http.json`
3. El workflow se importará automáticamente

### Paso 3: Verificar Configuración

1. Haz clic en el nodo **"Ejecutar vía HTTP"**
2. Verifica que la URL sea: `http://localhost:8000/execute`
3. El comando ya está configurado en el body JSON

### Paso 4: Probar

1. Asegúrate de que el servidor webhook esté corriendo
2. En n8n, haz clic en **"Execute Workflow"**
3. Verifica que el nodo HTTP se ejecute correctamente
4. Revisa los logs del servidor webhook para ver la ejecución

### Paso 5: Activar

1. Activa el toggle **"Active"** en n8n
2. El workflow se ejecutará automáticamente según el horario

---

## 🔄 Mantener Servidor Corriendo

### Opción 1: Terminal Abierta (Desarrollo)

Simplemente deja la terminal abierta con el servidor corriendo.

### Opción 2: Screen (Recomendado)

```bash
# Crear sesión screen
screen -S informessi-webhook

# Iniciar servidor
cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi
bash scripts/start-webhook.sh

# Detach: Ctrl+A, luego D
# Reattach: screen -r informessi-webhook
```

### Opción 3: systemd (Producción)

Crea `/etc/systemd/system/informessi-webhook.service`:

```ini
[Unit]
Description=InforMessi Webhook Server
After=network.target

[Service]
Type=simple
User=sebastian-mesch-henriques
WorkingDirectory=/home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi
ExecStart=/home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi/venv/bin/python3 /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi/scripts/webhook-server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Luego:
```bash
sudo systemctl enable informessi-webhook
sudo systemctl start informessi-webhook
sudo systemctl status informessi-webhook
```

---

## 🧪 Probar Manualmente

Puedes probar el webhook manualmente:

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi && bash scripts/daily-flow.sh"}'
```

---

## 📊 Monitoreo

### Ver Logs del Servidor

El servidor muestra logs en tiempo real:
- ✅ Ejecuciones exitosas
- ❌ Errores
- 📝 Comandos ejecutados

### Ver Logs en n8n

1. Ve a **"Executions"** en n8n
2. Revisa las ejecuciones del workflow
3. Ver detalles del nodo HTTP

---

## 🆘 Troubleshooting

### Servidor no responde

1. Verifica que esté corriendo:
   ```bash
   curl http://localhost:8000/
   ```
   Debería responder: `{"status": "ok", ...}`

2. Verifica el puerto:
   ```bash
   netstat -tuln | grep 8000
   ```

### Error 500 en n8n

1. Revisa los logs del servidor webhook
2. Verifica que el script `daily-flow.sh` exista
3. Verifica permisos de ejecución

### Workflow no se ejecuta

1. Verifica que el servidor webhook esté corriendo
2. Verifica la URL en el nodo HTTP
3. Prueba manualmente con curl

---

## ✅ Ventajas de esta Solución

- ✅ Funciona con cualquier versión de n8n
- ✅ No requiere módulos especiales
- ✅ Logs separados del servidor
- ✅ Fácil de debuggear
- ✅ Puede ejecutar cualquier comando

---

**Esta es la solución más robusta y compatible** 🚀

