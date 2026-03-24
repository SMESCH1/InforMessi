# Checklist de Configuración - InforMessi

Lista de verificación para dejar el sistema completamente funcional.

## ✅ Configuración Básica

### 1. Variables de Entorno Locales (`.env`)

Asegúrate de tener configurado en tu `.env` local:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_PREVIEW_CHAT_ID=tu_chat_privado_id
TELEGRAM_PUBLIC_CHAT_ID=tu_grupo_publico_id

# APIs
NEWSAPI_KEY=tu_newsapi_key

# Reddit (Opcional)
REDDIT_CLIENT_ID=tu_reddit_client_id
REDDIT_CLIENT_SECRET=tu_reddit_secret
REDDIT_USER_AGENT=tu_user_agent
```

**Estado:** ⬜ Configurado

---

### 2. Secrets de GitHub Actions

Configura los secrets en GitHub:

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Agrega cada uno:

```
TELEGRAM_BOT_TOKEN
TELEGRAM_PREVIEW_CHAT_ID
TELEGRAM_PUBLIC_CHAT_ID
NEWSAPI_KEY
GROQ_API_KEY
REDDIT_CLIENT_ID (opcional)
REDDIT_CLIENT_SECRET (opcional)
REDDIT_USER_AGENT (opcional)
```

**Estado:** ⬜ Configurado

**Verificar:**
- Ve a **Actions** → **InforMessi - Flujo Diario Completo**
- Click **Run workflow** (manual)
- Verifica que no haya errores de variables faltantes

---

### 3. Chat IDs de Telegram

**Chat Privado (Revisión):**
- Asegúrate de que el bot esté agregado al chat privado
- Obtén el Chat ID:
  ```bash
  python3 scripts/get-telegram-chat-id.py
  ```
- Agrega el ID a `.env` y a GitHub Secrets

**Grupo Público:**
- Asegúrate de que el bot esté agregado al grupo público
- El bot debe tener permisos para enviar mensajes
- Obtén el Chat ID (será un número negativo)
- Agrega el ID a `.env` y a GitHub Secrets

**Estado:** ⬜ Chat privado configurado | ⬜ Grupo público configurado

---

### 4. Generar Informes Anticipados

Genera informes para los próximos días:

```bash
# Generar informes para los próximos 15 días
python3 scripts/generate-advance-reports.py --days 15
```

Esto creará archivos en `reports/YYYY-MM-DD.json` para cada día.

**Estado:** ⬜ Informes generados

**Verificar:**
```bash
ls -la reports/ | head -20
```

---

### 5. Probar el Flujo Completo Localmente

**Paso 1: Actualizar informe del día**
```bash
python3 scripts/update-today-report.py
```

**Paso 2: Enviar a revisión**
```bash
python3 scripts/send-daily-report-review.py
```

**Paso 3: Verificar en Telegram**
- Deberías recibir el mensaje en tu chat privado
- Verifica que los botones funcionen

**Paso 4: Probar aprobación**
- Haz click en "✅ Aprobar" en Telegram
- Si tienes `TELEGRAM_PUBLIC_CHAT_ID` configurado, debería publicarse automáticamente
- Si no, usa:
  ```bash
  python3 scripts/publish-approved-report.py
  ```

**Estado:** ⬜ Flujo probado localmente

---

## 🔧 Configuración Opcional (Webhook para Aprobación Automática)

### 6. Desplegar Servidor Webhook (Opcional)

Si quieres que la aprobación funcione sin tener la PC prendida:

**Opción A: Railway (Recomendado)**
1. Ve a https://railway.app
2. Sign up con GitHub
3. New Project → Deploy from GitHub repo
4. Selecciona tu repo
5. Configura variables de entorno (mismas que en `.env`)
6. Railway generará una URL automáticamente
7. Configura el webhook:
   ```bash
   python3 scripts/setup-webhook.py --webhook-url https://tu-proyecto.up.railway.app
   ```

**Ver documentación completa:** `docs/webhook-hosting-gratis.md`

**Estado:** ⬜ Webhook desplegado | ⬜ Webhook configurado en Telegram

**Verificar:**
```bash
python3 scripts/setup-webhook.py --info
```

---

## 📋 Verificación Final

### Checklist de Verificación

- [ ] `.env` local configurado con todas las variables
- [ ] GitHub Secrets configurados
- [ ] Chat IDs de Telegram obtenidos y configurados
- [ ] Bot agregado a ambos chats (privado y público)
- [ ] Informes anticipados generados (al menos 15 días)
- [ ] Flujo probado localmente
- [ ] Workflow de GitHub Actions probado manualmente
- [ ] (Opcional) Webhook desplegado y configurado

---

## 🧪 Probar GitHub Actions

1. Ve a tu repositorio en GitHub
2. **Actions** → **InforMessi - Flujo Diario Completo**
3. Click **Run workflow**
4. Selecciona la rama (ej: `main` o `mvp-v1-generacion-anticipada`)
5. Click **Run workflow**
6. Espera a que termine
7. Verifica:
   - El informe se actualizó
   - Se envió a Telegram
   - Los cambios se committearon (si hubo cambios)

---

## ⚠️ Problemas Comunes

### El workflow falla

**Error: "Token de Telegram no encontrado"**
- Verifica que `TELEGRAM_BOT_TOKEN` esté en GitHub Secrets
- Verifica que el nombre del secret sea exactamente `TELEGRAM_BOT_TOKEN`

**Error: "Chat ID no encontrado"**
- Verifica que `TELEGRAM_PREVIEW_CHAT_ID` y `TELEGRAM_PUBLIC_CHAT_ID` estén en GitHub Secrets
- Verifica que los IDs sean correctos (números, pueden ser negativos para grupos)

**Error: "No se encontró informe"**
- Genera informes anticipados: `python3 scripts/generate-advance-reports.py --days 15`
- Haz commit y push de los informes generados

### El mensaje no llega a Telegram

- Verifica que el bot esté agregado a ambos chats
- Verifica que el bot tenga permisos para enviar mensajes
- Verifica que los Chat IDs sean correctos

### Los botones no funcionan

- Si usas webhook: verifica que esté configurado correctamente
- Si no usas webhook: los botones solo funcionan si tienes un script esperando (con `send-daily-report-review-wait.py`)

---

## 📅 Horario Configurado

- **Ejecución diaria:** 10:15 AM Argentina (13:15 UTC)
- **Workflow:** `.github/workflows/daily-informessi.yml`

---

## 🎯 Estado Actual del Sistema

Una vez completado este checklist, el sistema debería:

1. ✅ Ejecutarse automáticamente todos los días a las 10:15 AM Argentina
2. ✅ Actualizar el informe del día con datos recientes
3. ✅ Enviar el mensaje a Telegram (chat privado) para revisión
4. ✅ Permitir aprobación/rechazo/edición desde Telegram
5. ✅ Publicar automáticamente en el grupo público al aprobar (si está configurado)

---

## 📚 Documentación de Referencia

- [Configuración de GitHub Actions](github-actions-setup.md)
- [Configuración de Telegram](configuracion-telegram-dos-chats.md)
- [Flujo Automático con Aprobación](flujo-automatico-aprobacion.md)

