# Solución: Token del Bot Inválido

## 🔴 Problema

El token del bot está inválido (error 401), lo que causa:
- ❌ Los botones de aprobar/rechazar/editar no funcionan
- ❌ El webhook no puede procesar callbacks
- ❌ El workflow puede fallar al enviar mensajes

## ✅ Solución Paso a Paso

### Paso 1: Obtener el Token Correcto

1. Abre Telegram
2. Habla con `@BotFather`
3. Usa el comando `/token` para ver tu token actual
4. O si necesitas crear un nuevo bot: `/newbot`
5. Copia el token completo

### Paso 2: Actualizar Token en .env Local

1. Abre el archivo `.env` en la raíz del proyecto
2. Busca `TELEGRAM_BOT_TOKEN`
3. Reemplaza el valor:
   ```
   TELEGRAM_BOT_TOKEN=tu_nuevo_token_aqui
   ```
4. Guarda el archivo

### Paso 3: Verificar que Funcione Localmente

```bash
python3 scripts/verify-bot-token.py
```

Debería mostrar "✅ Token válido" con la información del bot.

### Paso 4: Actualizar Token en GitHub Secrets

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Busca `TELEGRAM_BOT_TOKEN`
4. Click en "Update"
5. Pega el nuevo token
6. Guarda

### Paso 5: Actualizar Token en Render

1. Ve a Render → Tu servicio webhook
2. Click en "Environment"
3. Busca `TELEGRAM_BOT_TOKEN`
4. Edita con el nuevo token
5. Guarda cambios (Render reiniciará automáticamente)

### Paso 6: Reconfigurar el Webhook

Una vez que el token esté actualizado en todos lados:

```bash
python3 scripts/setup-webhook.py --webhook-url https://tu-webhook.onrender.com
```

### Paso 7: Verificar que Todo Funcione

```bash
# Verificar token
python3 scripts/verify-bot-token.py

# Diagnosticar webhook
python3 scripts/diagnose-webhook-issue.py

# Probar el flujo
python3 scripts/send-daily-report-review.py
```

## 🔍 Verificación del Workflow

El workflow `daily-informessi.yml` está configurado para ejecutarse a las **13:15 UTC** (10:15 AM Argentina).

Para verificar si se ejecutó:
1. Ve a GitHub → Actions
2. Busca "InforMessi - Flujo Diario Completo"
3. Verifica las ejecuciones del día

Si no se ejecutó automáticamente:
- Puede ser que GitHub Actions tenga un delay
- Puede ser que el workflow esté deshabilitado
- Puedes ejecutarlo manualmente con "Run workflow"

## 📋 Checklist

- [ ] Token obtenido de @BotFather
- [ ] Token actualizado en `.env` local
- [ ] Token verificado con `verify-bot-token.py`
- [ ] Token actualizado en GitHub Secrets
- [ ] Token actualizado en Render
- [ ] Webhook reconfigurado
- [ ] Webhook verificado con `diagnose-webhook-issue.py`
- [ ] Flujo probado con `send-daily-report-review.py`
- [ ] Botones funcionan correctamente

## 🐛 Si los Botones Siguen Sin Funcionar

1. **Verifica los logs de Render:**
   - Ve a Render → Tu servicio → Logs
   - Haz clic en un botón en Telegram
   - Revisa si aparece algún log en Render

2. **Verifica que el webhook esté activo:**
   ```bash
   curl https://tu-webhook.onrender.com/health
   ```
   Debería responder con `{"status": "ok"}`

3. **Verifica que el webhook esté configurado en Telegram:**
   ```bash
   python3 scripts/setup-webhook.py --info
   ```

4. **Prueba manualmente:**
   - Ejecuta `python3 scripts/send-daily-report-review.py`
   - Haz clic en un botón
   - Revisa los logs de Render inmediatamente

