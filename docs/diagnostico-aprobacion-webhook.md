# Diagnóstico: Aprobación no Publica en Grupo Público

Guía para diagnosticar por qué al aprobar en el grupo preview no se publica en el grupo público.

## 🔍 Checklist de Diagnóstico

### 1. Verificar Webhook Configurado

```bash
python3 scripts/test-webhook-approval.py
```

O verificar manualmente:
```bash
python3 scripts/setup-webhook.py --info
```

### 2. Verificar TELEGRAM_PUBLIC_CHAT_ID en Render

1. Ve a Render → Tu servicio → **Environment**
2. Verifica que `TELEGRAM_PUBLIC_CHAT_ID` esté configurado
3. Verifica que el valor sea correcto (sin espacios, sin comillas)
4. Debe ser un número negativo para grupos (ej: `-1001234567890`)

### 3. Revisar Logs de Render

1. Ve a Render → Tu servicio → **Logs**
2. Click en "Aprobar" en el grupo preview
3. Inmediatamente revisa los logs
4. Busca mensajes que empiecen con:
   - `📥 Callback recibido`
   - `✅ Procesando aprobación...`
   - `📤 Intentando publicar...`
   - `❌ Error al publicar`

### 4. Verificar Permisos del Bot

1. Abre Telegram
2. Ve al grupo público
3. Verifica que el bot esté agregado
4. Verifica que el bot tenga permisos para enviar mensajes

## 🐛 Problemas Comunes

### Problema 1: TELEGRAM_PUBLIC_CHAT_ID no configurado

**Síntoma**: En los logs de Render ves:
```
⚠️ TELEGRAM_PUBLIC_CHAT_ID no configurado en Render
```

**Solución**:
1. Ve a Render → Environment
2. Agrega `TELEGRAM_PUBLIC_CHAT_ID` con el valor correcto
3. Guarda cambios (Render reiniciará automáticamente)

### Problema 2: Chat ID incorrecto

**Síntoma**: En los logs ves:
```
⚠️ TELEGRAM_PUBLIC_CHAT_ID está vacío o inválido
```

**Solución**:
1. Obtén el Chat ID correcto:
   ```bash
   python3 scripts/get-chat-id-from-url.py
   ```
2. Actualiza en Render con el valor correcto

### Problema 3: Bot no está en el grupo

**Síntoma**: En los logs ves:
```
Error: chat not found
```

**Solución**:
1. Abre Telegram
2. Ve al grupo público
3. Agrega el bot al grupo

### Problema 4: Bot sin permisos

**Síntoma**: En los logs ves:
```
Error: not enough rights
```

**Solución**:
1. Ve al grupo en Telegram
2. Configuración → Administradores
3. Verifica que el bot pueda enviar mensajes

### Problema 5: Webhook no recibe el callback

**Síntoma**: No ves ningún log cuando clickeas "Aprobar"

**Solución**:
1. Verifica que el webhook esté configurado:
   ```bash
   python3 scripts/setup-webhook.py --info
   ```
2. Verifica que el servicio en Render esté activo
3. El servicio puede tardar 30-60s en "despertar" si está dormido

## 📋 Pasos de Diagnóstico Detallado

### Paso 1: Verificar Configuración Local

```bash
# Verificar variables
python3 scripts/test-webhook-approval.py

# Verificar webhook
python3 scripts/setup-webhook.py --info
```

### Paso 2: Verificar en Render

1. Ve a Render → Tu servicio → **Environment**
2. Verifica estas variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_PREVIEW_CHAT_ID`
   - `TELEGRAM_PUBLIC_CHAT_ID` ← **IMPORTANTE**

### Paso 3: Probar Aprobación

1. Envía un mensaje al bot en el grupo preview
2. Click en "Aprobar"
3. **Inmediatamente** ve a Render → Logs
4. Revisa los logs para ver qué pasó

### Paso 4: Interpretar Logs

**Si ves esto en los logs:**
```
📥 Callback recibido: approve:...
✅ Procesando aprobación...
📤 Intentando publicar en grupo público...
✅ Mensaje publicado exitosamente
```
→ **Todo está funcionando correctamente**

**Si ves esto:**
```
📥 Callback recibido: approve:...
✅ Procesando aprobación...
❌ TELEGRAM_PUBLIC_CHAT_ID no configurado en Render
```
→ **Falta configurar TELEGRAM_PUBLIC_CHAT_ID en Render**

**Si ves esto:**
```
📥 Callback recibido: approve:...
✅ Procesando aprobación...
📤 Intentando publicar...
❌ Error al publicar: chat not found
```
→ **El bot no está en el grupo o el Chat ID es incorrecto**

## 🔧 Solución Rápida

1. **Verifica Render Environment**:
   - `TELEGRAM_PUBLIC_CHAT_ID` debe estar configurado
   - Valor correcto (sin espacios, sin comillas)
   - Número negativo para grupos

2. **Reinicia el servicio en Render**:
   - Render → Tu servicio → **Manual Deploy** → **Deploy latest commit**

3. **Prueba de nuevo**:
   - Envía mensaje al bot
   - Click en "Aprobar"
   - Revisa logs inmediatamente

## 💡 Tips

- **Los logs de Render son en tiempo real**: Revisa inmediatamente después de clickear "Aprobar"
- **El servicio puede estar dormido**: La primera request puede tardar 30-60s
- **Verifica el Chat ID**: Debe ser exactamente el mismo que obtienes con `get-chat-id-from-url.py`

---

**Si el problema persiste, comparte los logs de Render después de clickear "Aprobar".**



