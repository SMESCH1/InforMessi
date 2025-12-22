# Guía Rápida: Configurar n8n para InforMessi

Guía paso a paso para tener n8n funcionando en 5 minutos.

## 🚀 Inicio Rápido

### Opción 1: Script Automático

```bash
bash scripts/setup-n8n.sh
```

El script te guiará paso a paso.

### Opción 2: Manual

#### Paso 1: Instalar n8n

**Con Docker (Recomendado)**:
```bash
# Crear directorio de datos
mkdir -p ~/n8n-data

# Ejecutar n8n
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v ~/n8n-data:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=tu_password \
  n8nio/n8n
```

**Con npm**:
```bash
npm install n8n -g
n8n start
```

**Con npx** (sin instalación):
```bash
npx n8n
```

#### Paso 2: Acceder a n8n

1. Abre http://localhost:5678
2. Si usaste Docker con autenticación:
   - Usuario: `admin`
   - Contraseña: la que configuraste
3. Si es primera vez, crea una cuenta

#### Paso 3: Importar Workflow

1. En n8n, ve a **"Workflows"** → **"Import from File"**
2. Selecciona: `n8n/workflows/daily-informessi-simple.json`
3. El workflow se importará automáticamente

#### Paso 4: Configurar Credenciales

1. Haz clic en el nodo **"Ejecutar Flujo Completo"**
2. Verifica que la ruta sea correcta:
   ```
   /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi
   ```
3. Si es diferente, ajusta la ruta en el comando

#### Paso 5: Configurar Variables de Entorno (Opcional)

Si quieres usar variables de entorno en n8n:

1. Ve a **"Settings"** → **"Variables"**
2. Agrega:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_PREVIEW_CHAT_ID`
   - `TELEGRAM_PUBLISH_CHAT_ID`
   - `NEWSAPI_KEY` (opcional)

**Nota**: El script `daily-flow.sh` ya carga las variables desde `.env`, así que esto es opcional.

#### Paso 6: Ajustar Horario

1. Haz clic en el nodo **"Cron Trigger (8:00 AM)"**
2. Cambia la expresión cron si quieres otro horario:
   - `0 8 * * *` = 8:00 AM todos los días
   - `0 7 * * 1-5` = 7:00 AM lunes a viernes
   - `0 9 * * *` = 9:00 AM todos los días

#### Paso 7: Probar Workflow

1. Haz clic en **"Execute Workflow"** (botón arriba)
2. Verifica que todos los nodos se ejecuten correctamente
3. Revisa los logs de cada nodo
4. Verifica que el mensaje llegue a Telegram

#### Paso 8: Activar Workflow

1. Activa el toggle **"Active"** en la parte superior
2. El workflow se ejecutará automáticamente según el horario configurado

---

## 🧪 Probar Manualmente

Antes de activar, prueba que todo funcione:

```bash
# Ejecutar el flujo manualmente
cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi
bash scripts/daily-flow.sh
```

Si funciona, n8n también debería funcionar.

---

## 📊 Monitoreo

### Ver Ejecuciones

1. Ve a **"Executions"** en n8n
2. Verás todas las ejecuciones pasadas
3. Haz clic en una para ver detalles

### Logs en Tiempo Real

- Cada nodo muestra logs cuando se ejecuta
- Puedes ver errores y advertencias
- Los logs se guardan automáticamente

---

## 🔧 Troubleshooting

### n8n no inicia

```bash
# Ver si está corriendo (Docker)
docker ps | grep n8n

# Ver logs (Docker)
docker logs n8n

# Reiniciar (Docker)
docker restart n8n
```

### Workflow no se ejecuta

1. Verifica que esté **activado** (toggle "Active")
2. Verifica la expresión cron
3. Revisa los logs de ejecución

### Script falla en n8n

1. Ejecuta el script manualmente para ver el error:
   ```bash
   bash scripts/daily-flow.sh
   ```

2. Verifica rutas absolutas en el nodo
3. Verifica que las variables de entorno estén cargadas

### Puerto 5678 ocupado

```bash
# Ver qué está usando el puerto
sudo lsof -i :5678

# Cambiar puerto en Docker
docker run -p 5679:5678 ...  # Usa 5679 en lugar de 5678
```

---

## 📝 Comandos Útiles

### Docker

```bash
# Iniciar n8n
docker start n8n

# Detener n8n
docker stop n8n

# Ver logs
docker logs -f n8n

# Reiniciar n8n
docker restart n8n

# Eliminar n8n (cuidado: borra datos)
docker rm -f n8n
```

### npm/npx

```bash
# Iniciar n8n
n8n start

# Iniciar con logs detallados
n8n start --log-level=debug
```

---

## ✅ Checklist

- [ ] n8n instalado y corriendo
- [ ] Acceso a http://localhost:5678
- [ ] Workflow importado
- [ ] Ruta del script verificada
- [ ] Horario configurado
- [ ] Workflow probado manualmente
- [ ] Workflow activado
- [ ] Primera ejecución automática exitosa

---

**¡Listo! Tu automatización está configurada** 🎉

