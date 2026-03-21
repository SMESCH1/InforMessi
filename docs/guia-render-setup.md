# Guía de Configuración en Render - InforMessi

Guía paso a paso para desplegar el servidor webhook en Render.

## 🎯 Objetivo

Desplegar `scripts/webhook-server.py` en Render para que funcione 24/7 y permita aprobación automática sin tener la PC prendida.

## ✅ Paso 1: Crear Cuenta en Render

1. Ve a https://render.com
2. Click en **Sign Up**
3. Elige **Sign up with GitHub** (recomendado)
4. Autoriza Render para acceder a tu cuenta de GitHub

## ✅ Paso 2: Crear Nuevo Web Service

1. En el dashboard de Render, click en **New +**
2. Selecciona **Web Service**
3. Click en **Connect account** si es la primera vez
4. Selecciona tu repositorio de GitHub (InforMessi)
5. Click **Connect**

## ✅ Paso 3: Configurar el Servicio

Completa el formulario con estos valores:

### Información Básica

- **Name**: `informessi-webhook` (o el nombre que prefieras)
- **Region**: Elige la más cercana (ej: `Oregon (US West)` para mejor latencia)
- **Branch**: `main` (o la rama que uses)
- **Root Directory**: Dejar vacío (o `.` si Render lo requiere)

### Build & Deploy

- **Environment**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  python3 scripts/webhook-server.py
  ```

### Variables de Entorno

Click en **Advanced** → **Add Environment Variable** y agrega:

```
TELEGRAM_BOT_TOKEN = tu_token_aqui
TELEGRAM_PREVIEW_CHAT_ID = tu_chat_privado_id
TELEGRAM_PUBLIC_CHAT_ID = tu_grupo_publico_id
NEWSAPI_KEY = tu_newsapi_key
```

**Opcionales:**
```
OPENWEATHER_API_KEY = tu_openweather_key
REDDIT_CLIENT_ID = tu_reddit_client_id
REDDIT_CLIENT_SECRET = tu_reddit_secret
REDDIT_USER_AGENT = tu_user_agent
```

⚠️ **IMPORTANTE**: Usa los mismos valores que tienes en tu `.env` local.

### Plan

- Selecciona **Free** (tier gratuito)

## ✅ Paso 4: Crear el Servicio

1. Click en **Create Web Service**
2. Render comenzará a construir y desplegar el servicio
3. Espera 2-3 minutos mientras se despliega
4. Verás los logs en tiempo real

## ✅ Paso 5: Obtener la URL

Una vez desplegado:

1. En el dashboard de tu servicio, verás una URL como:
   ```
   https://informessi-webhook.onrender.com
   ```
2. **Copia esta URL** - la necesitarás para configurar el webhook

## ✅ Paso 6: Configurar Webhook en Telegram

Desde tu PC local (con `.env` configurado):

```bash
# Configurar webhook
python3 scripts/setup-webhook.py --webhook-url https://informessi-webhook.onrender.com
```

O manualmente:

```bash
TOKEN="tu_telegram_bot_token"
WEBHOOK_URL="https://informessi-webhook.onrender.com"

curl -X POST "https://api.telegram.org/bot${TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${WEBHOOK_URL}/webhook\"}"
```

## ✅ Paso 7: Verificar que Funciona

### Verificar Webhook

```bash
python3 scripts/setup-webhook.py --info
```

Deberías ver:
```
📋 Información del Webhook:
   URL: https://informessi-webhook.onrender.com/webhook
   Pending updates: 0
```

### Probar el Servidor

```bash
curl https://informessi-webhook.onrender.com/health
```

Debería responder:
```json
{
  "status": "ok",
  "service": "InforMessi Webhook",
  "timestamp": "2025-12-28T..."
}
```

### Probar Aprobación

1. Ejecuta el workflow de GitHub Actions o envía un mensaje manualmente:
   ```bash
   python3 scripts/send-daily-report-review.py
   ```
2. En Telegram, haz click en "✅ Aprobar"
3. Debería publicarse automáticamente en el grupo público

## ⚠️ Limitaciones de Render (Free Tier)

### "Sleep" después de inactividad

- Render "duerme" el servicio después de **15 minutos de inactividad**
- Cuando llega un request, tarda **30-60 segundos** en "despertar"
- Esto es normal y no afecta la funcionalidad

### Soluciones

1. **Usar un servicio de "ping"** (opcional):
   - Configura un cron job que haga ping cada 10 minutos
   - O usa un servicio como https://cron-job.org
   - Ping a: `https://informessi-webhook.onrender.com/health`

2. **Aceptar el delay**:
   - El delay de 30-60 segundos es aceptable para la mayoría de casos
   - Los callbacks de Telegram se procesarán cuando el servicio despierte

## 🔧 Troubleshooting

### El servicio no inicia

**Error: "Module not found"**
- Verifica que `requirements.txt` incluya `flask`
- Revisa los logs en Render

**Error: "Port not found"**
- Render asigna el puerto automáticamente
- El script `webhook-server.py` usa `os.getenv('PORT')` que Render proporciona automáticamente

### El webhook no funciona

**Verifica que el webhook esté configurado:**
```bash
python3 scripts/setup-webhook.py --info
```

**Verifica los logs en Render:**
- Ve a tu servicio en Render
- Click en **Logs**
- Deberías ver requests cuando haces click en los botones

**Verifica variables de entorno:**
- Asegúrate de que todas las variables estén configuradas en Render
- Los nombres deben ser exactos (mayúsculas/minúsculas)

### El servicio se "duerme" mucho

- Esto es normal en el free tier
- Considera usar un servicio de ping (ver arriba)
- O actualiza a un plan de pago si necesitas 24/7 sin delays

## 📋 Checklist Final

- [ ] Cuenta creada en Render
- [ ] Web Service creado y configurado
- [ ] Variables de entorno agregadas
- [ ] Servicio desplegado exitosamente
- [ ] URL obtenida
- [ ] Webhook configurado en Telegram
- [ ] Webhook verificado (`--info`)
- [ ] Servidor verificado (`/health`)
- [ ] Aprobación probada y funcionando

## 🎉 ¡Listo!

Una vez completado, el sistema funcionará así:

1. GitHub Actions envía mensaje a Telegram
2. Tú haces click en "✅ Aprobar" (desde móvil o PC)
3. Render procesa el callback
4. Se publica automáticamente en el grupo público
5. ✅ **Todo sin tener la PC prendida**

---

**Nota**: Si Render se "duerme", el primer callback tardará 30-60 segundos en procesarse, pero funcionará correctamente.

