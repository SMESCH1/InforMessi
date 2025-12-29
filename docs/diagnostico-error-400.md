# Diagnóstico Error 400 al Publicar - InforMessi

Guía para diagnosticar y resolver el error 400 al publicar en el grupo público.

## 🔍 Error Común

```
❌ Error al publicar: 400 Client Error: Bad Request for url: https://api.telegram.org/bot.../sendMessage
```

## 🔧 Causas Posibles

### 1. Chat ID Incorrecto

**Síntoma**: Error 400 con descripción "chat not found" o "bad request"

**Solución**:
- Verifica que `TELEGRAM_PUBLIC_CHAT_ID` en Render sea correcto
- Debe ser un número negativo para grupos (ej: `-5227996854`)
- No debe tener espacios ni caracteres extra

**Cómo verificar**:
```bash
python3 scripts/get-telegram-chat-id.py
```

### 2. Bot No Está en el Grupo

**Síntoma**: Error 400 con descripción "chat not found"

**Solución**:
1. Abre el grupo público en Telegram
2. Verifica que el bot esté agregado
3. Si no está, agrégalo como miembro

### 3. Bot Sin Permisos

**Síntoma**: Error 400 con descripción "not enough rights" o similar

**Solución**:
1. En el grupo público, ve a **Configuración del grupo**
2. **Administradores** → Busca tu bot
3. Verifica que tenga permisos para:
   - ✅ Enviar mensajes
   - ✅ No necesita ser administrador, solo poder enviar

### 4. Mensaje Demasiado Largo

**Síntoma**: Error 400 (aunque el código ya valida esto)

**Solución**: El código ya trunca mensajes a 4096 caracteres, pero verifica que el mensaje no sea excesivamente largo.

### 5. Caracteres Especiales

**Síntoma**: Error 400 sin descripción clara

**Solución**: El código ya envía sin `parse_mode` para evitar problemas con HTML/emojis.

## 🧪 Pasos de Diagnóstico

### Paso 1: Verificar Chat ID

```bash
# Obtener Chat ID del grupo público
python3 scripts/get-telegram-chat-id.py
```

Asegúrate de:
- Enviar un mensaje en el grupo público
- El bot debe estar en el grupo
- Copiar el Chat ID (será negativo)

### Paso 2: Verificar en Render

1. Ve a Render → Tu servicio → **Environment**
2. Verifica `TELEGRAM_PUBLIC_CHAT_ID`:
   - Debe ser el número completo (ej: `-5227996854`)
   - Sin espacios
   - Sin comillas
   - Debe empezar con `-` si es un grupo

### Paso 3: Verificar Permisos del Bot

1. Abre Telegram
2. Ve al grupo público
3. Configuración → Administradores
4. Verifica que el bot pueda enviar mensajes

### Paso 4: Probar Manualmente

```bash
# Probar publicación manual
python3 scripts/publish-approved-report.py
```

Si funciona manualmente pero no desde Render, el problema es la configuración en Render.

## 🔧 Solución Rápida

### Si el error persiste:

1. **Verifica el Chat ID en Render**:
   - Debe ser exactamente el mismo que obtienes con `get-telegram-chat-id.py`
   - Debe ser un número (puede ser negativo)

2. **Reinicia el servicio en Render**:
   - Render → Tu servicio → **Manual Deploy** → **Deploy latest commit**

3. **Verifica los logs en Render**:
   - Render → Tu servicio → **Logs**
   - Busca el error completo con detalles

4. **Prueba con un mensaje simple**:
   ```python
   # Desde Python
   import requests
   token = "TU_TOKEN"
   chat_id = "TU_CHAT_ID"
   url = f"https://api.telegram.org/bot{token}/sendMessage"
   data = {"chat_id": chat_id, "text": "Test"}
   response = requests.post(url, json=data)
   print(response.json())
   ```

## 📋 Checklist

- [ ] Chat ID es correcto (número negativo para grupos)
- [ ] Chat ID está configurado en Render sin espacios
- [ ] Bot está agregado al grupo público
- [ ] Bot tiene permisos para enviar mensajes
- [ ] Servicio en Render está activo
- [ ] Variables de entorno en Render son correctas

## 💡 Mensaje de Error Mejorado

El código ahora muestra:
- Detalle del error de Telegram
- Código de error
- Chat ID usado (primeros 20 caracteres)
- Checklist de verificación

Esto te ayudará a identificar exactamente qué está fallando.

