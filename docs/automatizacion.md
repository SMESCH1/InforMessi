# Automatización - InforMessi

Guía para configurar la automatización diaria del sistema InforMessi.

## 🎯 Opciones de Automatización

Tienes dos opciones:

1. **n8n** (Recomendado para portfolio) - Workflow visual, más robusto
2. **Cron** (Simple) - Más básico, fácil de configurar

---

## 📋 Opción 1: n8n (Recomendado)

### Ventajas

- ✅ Workflow visual (mejor para portfolio)
- ✅ Manejo de errores más robusto
- ✅ Logs y monitoreo integrado
- ✅ Fácil de modificar sin editar código
- ✅ Integración con múltiples servicios

### Instalación

#### Opción A: Docker (Recomendado)

```bash
# Crear directorio para n8n
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

Accede a: http://localhost:5678

#### Opción B: npm

```bash
npm install n8n -g
n8n start
```

### Configurar Workflow

1. **Importar workflow**:
   - En n8n, ve a "Workflows" → "Import from File"
   - Selecciona: `n8n/workflows/daily-informessi-simple.json`

2. **Configurar credenciales**:
   - Telegram Bot: Agrega tus credenciales de Telegram
   - Variables de entorno: Configura en n8n Settings

3. **Ajustar ruta del script**:
   - Edita el nodo "Ejecutar Flujo Completo"
   - Ajusta la ruta si es necesario

4. **Activar workflow**:
   - Activa el workflow en n8n
   - Se ejecutará automáticamente a las 8:00 AM

### Workflows Disponibles

- **`daily-informessi-simple.json`**: Ejecuta el script completo (más simple)
- **`daily-informessi.json`**: Workflow detallado con pasos separados (más control)

---

## ⏰ Opción 2: Cron (Simple)

### Ventajas

- ✅ Muy simple de configurar
- ✅ No requiere servicios adicionales
- ✅ Funciona en cualquier Linux/Mac

### Configuración

#### Paso 1: Crear script de log

```bash
# Crear directorio de logs
mkdir -p ~/informessi-logs
```

#### Paso 2: Configurar cron

```bash
# Editar crontab
crontab -e

# Agregar esta línea (ejecuta a las 8:00 AM todos los días)
0 8 * * * cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi && bash scripts/daily-flow.sh >> ~/informessi-logs/cron-$(date +\%Y-\%m-\%d).log 2>&1
```

#### Paso 3: Verificar

```bash
# Ver crontab configurado
crontab -l

# Ver logs
tail -f ~/informessi-logs/cron-$(date +%Y-%m-%d).log
```

### Horarios Comunes

```bash
# 8:00 AM todos los días
0 8 * * * ...

# 7:30 AM todos los días
30 7 * * * ...

# 9:00 AM de lunes a viernes
0 9 * * 1-5 ...

# Cada 12 horas (8 AM y 8 PM)
0 8,20 * * * ...
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno en n8n

En n8n, configura estas variables de entorno:

```
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_PREVIEW_CHAT_ID=-123456789
TELEGRAM_PUBLISH_CHAT_ID=-987654321
NEWSAPI_KEY=tu_key (opcional)
```

### Notificaciones de Error

#### Con n8n

Agrega un nodo "On Error" que envíe notificación a Telegram si falla.

#### Con Cron

```bash
# Script con notificación de error
0 8 * * * cd /ruta/a/InforMessi && bash scripts/daily-flow.sh || echo "Error en InforMessi" | mail -s "Error" tu@email.com
```

---

## 🧪 Probar Automatización

### Probar Cron Manualmente

```bash
# Ejecutar el comando que cron ejecutaría
cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi
bash scripts/daily-flow.sh
```

### Probar n8n

1. En n8n, haz clic en "Execute Workflow"
2. Verifica que todos los nodos se ejecuten correctamente
3. Revisa los logs

---

## 📊 Monitoreo

### Logs de Cron

```bash
# Ver logs del día
cat ~/informessi-logs/cron-$(date +%Y-%m-%d).log

# Ver últimos logs
ls -lt ~/informessi-logs/ | head -5
```

### Logs de n8n

- Ve a "Executions" en n8n
- Revisa ejecuciones pasadas
- Ver detalles de cada ejecución

---

## 🆘 Troubleshooting

### Cron no ejecuta

1. Verificar que cron esté corriendo:
   ```bash
   sudo systemctl status cron  # Linux
   sudo launchctl list | grep cron  # Mac
   ```

2. Verificar permisos del script:
   ```bash
   chmod +x scripts/daily-flow.sh
   ```

3. Verificar ruta absoluta en crontab

### n8n no ejecuta

1. Verificar que n8n esté corriendo
2. Verificar que el workflow esté activado
3. Revisar logs de n8n
4. Verificar credenciales de Telegram

### Script falla

1. Ejecutar manualmente para ver error:
   ```bash
   bash scripts/daily-flow.sh
   ```

2. Verificar variables de entorno:
   ```bash
   export $(grep -v '^#' .env | grep -v '^$' | xargs)
   echo $TELEGRAM_BOT_TOKEN
   ```

---

## 📝 Recomendación

**Para portfolio**: Usa **n8n** (más visual, mejor para mostrar)

**Para uso personal simple**: Usa **cron** (más directo)

---

*Una vez configurado, el sistema se ejecutará automáticamente cada día*

