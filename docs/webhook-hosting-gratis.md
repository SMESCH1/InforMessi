# Hosting Gratuito para Webhook Server - InforMessi

Guía para desplegar el servidor webhook en servicios gratuitos.

## 🎯 Objetivo

Desplegar `scripts/webhook-server.py` en un servicio gratuito para que funcione 24/7 y permita aprobación automática sin tener la PC prendida.

## ✅ Opciones Gratuitas Recomendadas

### 1. **Railway** (Recomendado) ⭐

**Ventajas:**
- ✅ Tier gratuito generoso (500 horas/mes)
- ✅ Fácil de configurar
- ✅ Auto-deploy desde GitHub
- ✅ HTTPS incluido
- ✅ Variables de entorno fáciles

**Límites:**
- 500 horas/mes gratis (suficiente para 24/7)
- $5 de crédito gratis al mes

**Pasos:**
1. Ve a https://railway.app
2. Sign up con GitHub
3. New Project → Deploy from GitHub repo
4. Selecciona tu repo
5. Railway detectará automáticamente Python
6. Configura variables de entorno:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_PREVIEW_CHAT_ID`
   - `TELEGRAM_PUBLIC_CHAT_ID`
   - `PORT` (Railway lo asigna automáticamente)
7. Railway generará una URL como: `https://tu-proyecto.up.railway.app`
8. Configura webhook en Telegram (ver abajo)

---

### 2. **Render**

**Ventajas:**
- ✅ Tier gratuito (750 horas/mes)
- ✅ Fácil configuración
- ✅ HTTPS incluido

**Límites:**
- Se "duerme" después de 15 min de inactividad (se despierta con el primer request)
- Puede tardar 30-60 segundos en despertar

**Pasos:**
1. Ve a https://render.com
2. Sign up
3. New → Web Service
4. Conecta tu repo de GitHub
5. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 scripts/webhook-server.py`
   - **Environment**: Python 3
6. Agrega variables de entorno
7. Render generará una URL
8. Configura webhook en Telegram

---

### 3. **Fly.io**

**Ventajas:**
- ✅ Tier gratuito generoso
- ✅ No se duerme
- ✅ Muy rápido

**Límites:**
- Requiere tarjeta de crédito (pero no cobra si no excedes el free tier)
- Más complejo de configurar

**Pasos:**
1. Instala Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Crea app: `fly launch`
4. Configura `fly.toml`:
   ```toml
   app = "informessi-webhook"
   primary_region = "iad"
   
   [build]
   
   [http_service]
     internal_port = 5000
     force_https = true
     auto_stop_machines = false
     auto_start_machines = true
   ```
5. Deploy: `fly deploy`
6. Configura secrets: `fly secrets set TELEGRAM_BOT_TOKEN=xxx ...`

---

### 4. **Oracle Cloud (Siempre Gratis)**

**Ventajas:**
- ✅ Siempre gratis (sin límites de tiempo)
- ✅ VPS completo
- ✅ No se duerme

**Desventajas:**
- ⚠️ Más complejo de configurar
- ⚠️ Requiere tarjeta de crédito (pero no cobra si usas solo free tier)

**Pasos:**
1. Crea cuenta en https://cloud.oracle.com
2. Crea instancia "Always Free" (VM.Standard.A1.Flex)
3. SSH a la instancia
4. Instala Python y dependencias
5. Configura como servicio systemd
6. Configura nginx como reverse proxy
7. Configura webhook en Telegram

---

## 🔧 Configuración del Webhook en Telegram

Una vez que tengas la URL de tu servidor (ej: `https://tu-proyecto.up.railway.app`):

```bash
# Obtener tu bot token
TOKEN="tu_telegram_bot_token"

# Configurar webhook
curl -X POST "https://api.telegram.org/bot${TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://tu-proyecto.up.railway.app/webhook"}'

# Verificar webhook
curl "https://api.telegram.org/bot${TOKEN}/getWebhookInfo"
```

O usa este script:

```python
# scripts/setup-webhook.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
webhook_url = os.getenv("WEBHOOK_URL")  # URL de tu servidor

if not token or not webhook_url:
    print("❌ Configura TELEGRAM_BOT_TOKEN y WEBHOOK_URL en .env")
    sys.exit(1)

url = f"https://api.telegram.org/bot{token}/setWebhook"
data = {"url": f"{webhook_url}/webhook"}

response = requests.post(url, json=data)
print(response.json())
```

---

## 📋 Requisitos del Servidor

El servidor necesita:

1. **Python 3.8+**
2. **Dependencias**:
   ```
   flask
   requests
   python-dotenv
   ```
3. **Variables de entorno**:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_PREVIEW_CHAT_ID`
   - `TELEGRAM_PUBLIC_CHAT_ID`
   - `PORT` (asignado por el servicio)

---

## 🧪 Probar el Webhook

Una vez desplegado:

1. Verifica que el servidor esté activo:
   ```bash
   curl https://tu-proyecto.up.railway.app/health
   ```

2. Debería responder:
   ```json
   {
     "status": "ok",
     "service": "InforMessi Webhook",
     "timestamp": "2025-12-28T..."
   }
   ```

3. Prueba enviando un mensaje al bot en Telegram
4. Verifica los logs del servidor

---

## 🔄 Actualizar GitHub Actions

Una vez que el webhook esté funcionando, el workflow de GitHub Actions puede seguir usando `send-daily-report-review.py` (con `--no-wait`), y el webhook procesará las aprobaciones automáticamente.

---

## 💡 Recomendación

Para el MVP, **Railway** es la opción más fácil y rápida:
- ✅ Configuración en 5 minutos
- ✅ Auto-deploy desde GitHub
- ✅ HTTPS incluido
- ✅ Suficiente para el uso esperado

---

## 📚 Referencias

- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)
- [Telegram Bot API - Webhooks](https://core.telegram.org/bots/api#setwebhook)

