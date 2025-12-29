# Verificar Variables en Render - InforMessi

Guía para verificar y configurar correctamente las variables de entorno en Render.

## 🔍 Verificar Variables Actuales

1. Ve a tu servicio en Render: https://dashboard.render.com
2. Selecciona tu servicio `informessi-webhook`
3. Click en **Environment** (en el menú lateral)
4. Verifica que tengas estas variables:

### Variables Requeridas:

```
TELEGRAM_BOT_TOKEN = tu_token_completo
TELEGRAM_PREVIEW_CHAT_ID = tu_chat_privado_id
TELEGRAM_PUBLIC_CHAT_ID = tu_grupo_publico_id
NEWSAPI_KEY = tu_newsapi_key
```

### Cómo Verificar los Valores:

**TELEGRAM_BOT_TOKEN:**
- Debe ser el token completo del bot (ej: `***REMOVED***`)
- Obtenerlo de @BotFather en Telegram

**TELEGRAM_PREVIEW_CHAT_ID:**
- Debe ser el ID del chat privado (número positivo, ej: `123456789`)
- Obtenerlo con: `python3 scripts/get-telegram-chat-id.py`

**TELEGRAM_PUBLIC_CHAT_ID:**
- Debe ser el ID del grupo público (número negativo, ej: `-1001234567890`)
- ⚠️ **IMPORTANTE**: Debe empezar con `-` si es un grupo
- Obtenerlo con: `python3 scripts/get-telegram-chat-id.py`

## ✅ Agregar/Editar Variables

1. En Render, ve a **Environment**
2. Click en **Add Environment Variable** (o edita la existente)
3. **Name**: El nombre exacto (ej: `TELEGRAM_PUBLIC_CHAT_ID`)
4. **Value**: El valor completo
5. Click **Save Changes**
6. Render reiniciará automáticamente el servicio

## 🔧 Verificar que el Bot Tiene Permisos

1. Abre Telegram
2. Ve al grupo público
3. Verifica que el bot esté agregado
4. Verifica que el bot tenga permisos para:
   - ✅ Enviar mensajes
   - ✅ No necesita ser administrador, solo poder enviar mensajes

## 🧪 Probar Después de Configurar

1. Espera 1-2 minutos para que Render reinicie
2. Verifica que el servicio esté activo:
   ```bash
   curl https://informessi-webhook.onrender.com/health
   ```
3. Prueba el flujo de edición de nuevo

## ⚠️ Problemas Comunes

### "Bad Request" al publicar

**Causa**: Chat ID incorrecto o bot sin permisos

**Solución**:
1. Verifica que `TELEGRAM_PUBLIC_CHAT_ID` sea correcto
2. Asegúrate de que el bot esté en el grupo
3. Verifica permisos del bot en el grupo

### El webhook no responde

**Causa**: Servicio dormido o variables incorrectas

**Solución**:
1. Verifica que todas las variables estén configuradas
2. Revisa los logs en Render
3. El servicio puede tardar 30-60s en "despertar" si está dormido

### Variables no se cargan

**Causa**: Nombres incorrectos o valores con espacios

**Solución**:
1. Verifica que los nombres sean exactos (mayúsculas/minúsculas)
2. No dejes espacios al inicio o final del valor
3. Reinicia el servicio en Render después de cambiar variables

