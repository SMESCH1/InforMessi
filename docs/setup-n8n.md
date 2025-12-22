# Configuración de n8n - InforMessi

Guía paso a paso para configurar n8n y automatizar InforMessi.

## 📦 Instalación de n8n

### Opción 1: Docker (Recomendado)

```bash
# Crear directorio para datos de n8n
mkdir -p ~/n8n-data

# Ejecutar n8n
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/n8n-data:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=tu_password_seguro \
  n8nio/n8n
```

**Accede a**: http://localhost:5678

### Opción 2: npm

```bash
npm install n8n -g
n8n start
```

### Opción 3: npx (Sin instalación)

```bash
npx n8n
```

---

## 🔧 Configuración Inicial

### 1. Acceder a n8n

1. Abre http://localhost:5678
2. Crea una cuenta o inicia sesión
3. Completa el setup inicial

### 2. Configurar Credenciales

#### Telegram Bot

1. Ve a "Credentials" → "New"
2. Selecciona "Telegram"
3. Ingresa tu `TELEGRAM_BOT_TOKEN`
4. Guarda como "Telegram Bot"

### 3. Configurar Variables de Entorno

1. Ve a "Settings" → "Variables"
2. Agrega:
   - `TELEGRAM_PREVIEW_CHAT_ID`
   - `TELEGRAM_PUBLISH_CHAT_ID`
   - `NEWSAPI_KEY` (opcional)

---

## 📥 Importar Workflow

### Workflow Simple (Recomendado para empezar)

1. En n8n, ve a "Workflows" → "Import from File"
2. Selecciona: `n8n/workflows/daily-informessi-simple.json`
3. Ajusta la ruta del script si es necesario
4. Configura las credenciales de Telegram
5. Activa el workflow

### Workflow Detallado (Más control)

1. Importa: `n8n/workflows/daily-informessi.json`
2. Configura cada nodo según necesidad
3. Activa el workflow

---

## ⚙️ Ajustar Workflow

### Cambiar Horario

1. Edita el nodo "Cron Trigger"
2. Cambia la expresión cron:
   - `0 8 * * *` = 8:00 AM todos los días
   - `0 7 * * 1-5` = 7:00 AM lunes a viernes
   - `0 9 * * *` = 9:00 AM todos los días

### Cambiar Ruta del Script

1. Edita el nodo "Ejecutar Flujo Completo"
2. Ajusta la ruta en el comando:
   ```bash
   cd /ruta/a/InforMessi && bash scripts/daily-flow.sh
   ```

### Agregar Notificaciones de Error

1. Agrega un nodo "On Error"
2. Conecta a un nodo de Telegram
3. Configura para enviar notificación si falla

---

## 🧪 Probar Workflow

1. Haz clic en "Execute Workflow"
2. Verifica que todos los nodos se ejecuten
3. Revisa los logs de cada nodo
4. Verifica que el mensaje llegue a Telegram

---

## 📊 Monitoreo

### Ver Ejecuciones

1. Ve a "Executions" en n8n
2. Revisa ejecuciones pasadas
3. Ver detalles de cada ejecución

### Logs

- Cada nodo muestra logs en tiempo real
- Puedes ver errores y advertencias
- Los logs se guardan automáticamente

---

## 🔄 Mantener n8n Corriendo

### Con Docker

```bash
# Ejecutar en background
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v ~/n8n-data:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=tu_password \
  n8nio/n8n

# Ver logs
docker logs -f n8n

# Detener
docker stop n8n

# Iniciar
docker start n8n
```

### Con systemd (Linux)

Crea `/etc/systemd/system/n8n.service`:

```ini
[Unit]
Description=n8n
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/home/tu_usuario
ExecStart=/usr/bin/n8n start
Restart=always

[Install]
WantedBy=multi-user.target
```

Luego:
```bash
sudo systemctl enable n8n
sudo systemctl start n8n
```

---

## 🆘 Troubleshooting

### n8n no inicia

- Verifica que el puerto 5678 esté libre
- Revisa logs: `docker logs n8n` o `n8n --log-level=debug`

### Workflow no se ejecuta

- Verifica que esté activado
- Revisa la expresión cron
- Verifica credenciales

### Script falla en n8n

- Ejecuta el script manualmente para ver el error
- Verifica rutas absolutas
- Verifica variables de entorno

---

*n8n es ideal para automatización visual y presentación en portfolio*

