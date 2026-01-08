# Guía: Configurar Canal de Telegram

Esta guía explica cómo configurar InforMessi para usar un **canal de Telegram** en lugar de un grupo público.

---

## 📋 Diferencias entre Grupo y Canal

### Grupo
- Los miembros pueden escribir mensajes
- El bot puede enviar mensajes normalmente
- Chat ID: `-100XXXXXXXXX` (grupos) o `-XXXXXXXXX` (supergrupos)

### Canal
- Solo los administradores pueden publicar
- El bot **debe ser administrador** del canal
- Chat ID: `-100XXXXXXXXX` (canales privados) o `@nombre_canal` (canales públicos)
- Los mensajes aparecen como "publicados por el canal"

---

## ✅ Ventajas de Usar un Canal

1. **Más profesional**: Los mensajes aparecen como publicaciones oficiales
2. **Sin spam**: Los miembros no pueden escribir, solo leer
3. **Mejor para contenido**: Ideal para informes diarios
4. **Público o privado**: Puedes hacer el canal público con username

---

## 🚀 Configuración Paso a Paso

### Paso 1: Crear el Canal

1. Abre Telegram
2. Crea un **Nuevo Canal**
3. Elige un nombre (ej: "InforMessi - Informes Diarios")
4. Configura como **Público** (opcional, pero recomendado)
   - Si es público, elige un username (ej: `@informessi`)
5. Completa la creación

### Paso 2: Agregar el Bot como Administrador

1. Ve a la configuración del canal
2. **Administradores** → **Agregar Administrador**
3. Busca tu bot (ej: `@informessipruebabot`)
4. **Permisos importantes:**
   - ✅ **Publicar mensajes** (obligatorio)
   - ✅ **Editar mensajes** (opcional, útil para correcciones)
   - ❌ No necesita otros permisos

### Paso 3: Obtener el Chat ID del Canal

Tienes varias opciones:

#### Opción A: Usando el Bot (Recomendado)

```bash
# Enviar un mensaje al canal desde el bot
# Luego obtener el Chat ID
python3 scripts/get-telegram-chat-id.py
```

**Nota:** Si el canal es público, puedes usar directamente el username: `@nombre_canal`

#### Opción B: Desde la URL del Canal

Si el canal es público:
- URL: `https://t.me/nombre_canal`
- Chat ID: `@nombre_canal` (puedes usar esto directamente)

Si el canal es privado:
- Necesitas obtener el Chat ID numérico (usando el bot)

#### Opción C: Usando un Script

```bash
# Crear un mensaje de prueba en el canal
# Luego ejecutar:
python3 scripts/get-chat-id-from-url.py
```

### Paso 4: Configurar el Chat ID

Una vez que tengas el Chat ID del canal:

#### En `.env` (local)

```bash
# Editar .env
nano .env

# Cambiar o agregar:
TELEGRAM_PUBLIC_CHAT_ID=@nombre_canal
# O si es privado:
TELEGRAM_PUBLIC_CHAT_ID=-1001234567890
```

#### En GitHub Secrets

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Edita `TELEGRAM_PUBLIC_CHAT_ID`
4. Actualiza con el Chat ID del canal

#### En Render (Webhook)

1. Ve a tu servicio en Render
2. **Environment** → **Environment Variables**
3. Edita `TELEGRAM_PUBLIC_CHAT_ID`
4. Actualiza con el Chat ID del canal

### Paso 5: Verificar la Configuración

```bash
# Verificar que el bot puede publicar en el canal
python3 scripts/diagnose-workflow.py

# O probar envío directo:
python3 scripts/test-telegram.py
```

---

## 🔧 Cambios en el Código

**¡Buenas noticias!** El código actual **ya funciona con canales** sin cambios. La API de Telegram trata grupos y canales de la misma manera para `sendMessage` y `sendPhoto`.

### Lo que NO necesitas cambiar:

- ✅ `send-daily-report-review.py` - Funciona con canales
- ✅ `auto-publish-fallback.py` - Funciona con canales
- ✅ `webhook-server.py` - Funciona con canales
- ✅ Todos los scripts de publicación - Funcionan con canales

### Lo único que cambia:

- El valor de `TELEGRAM_PUBLIC_CHAT_ID` en la configuración

---

## 📝 Ejemplos de Configuración

### Canal Público

```env
# .env
TELEGRAM_PUBLIC_CHAT_ID=@informessi
```

**Ventajas:**
- Fácil de compartir (URL: `https://t.me/informessi`)
- No necesitas Chat ID numérico
- Más fácil de encontrar

### Canal Privado

```env
# .env
TELEGRAM_PUBLIC_CHAT_ID=-1001234567890
```

**Ventajas:**
- Más privado
- Solo miembros pueden ver

---

## ⚠️ Consideraciones Importantes

### 1. Permisos del Bot

El bot **debe ser administrador** del canal con permiso para **publicar mensajes**. Sin esto, recibirás errores como:

```
❌ Error: chat not found
❌ Error: not enough rights to send messages
```

### 2. Formato del Chat ID

- **Canal público**: Puedes usar `@nombre_canal` o el Chat ID numérico
- **Canal privado**: Debes usar el Chat ID numérico (`-100XXXXXXXXX`)

### 3. Mensajes Editados

Si quieres que el bot pueda editar mensajes en el canal:
- Dale permiso de **Editar mensajes** al bot
- El código actual no edita mensajes, solo publica nuevos

### 4. Webhooks

Los webhooks funcionan igual con canales. No necesitas cambiar nada en Render.

---

## 🧪 Probar la Configuración

### Test Rápido

```bash
# Verificar configuración
python3 scripts/diagnose-workflow.py

# Probar envío
python3 scripts/test-telegram.py
```

### Test Completo

```bash
# Simular workflow completo
bash scripts/test-workflow-manual.sh 2026-01-01
```

---

## 🔄 Migrar de Grupo a Canal

Si ya tienes un grupo configurado y quieres migrar a un canal:

1. **Crear el canal** (paso 1)
2. **Agregar el bot como administrador** (paso 2)
3. **Obtener Chat ID del canal** (paso 3)
4. **Actualizar `TELEGRAM_PUBLIC_CHAT_ID`** en:
   - `.env` (local)
   - GitHub Secrets
   - Render (si usas webhook)
5. **Probar** con `diagnose-workflow.py`

**Nota:** Los mensajes antiguos del grupo no se migran automáticamente.

---

## 📚 Referencias

- [Telegram Bot API - sendMessage](https://core.telegram.org/bots/api#sendmessage)
- [Telegram Bot API - sendPhoto](https://core.telegram.org/bots/api#sendphoto)
- [Guía: Obtener Chat ID](obtener-chat-id-sin-bots.md)

---

## 💡 Tips

1. **Canal público**: Usa `@nombre_canal` en la configuración (más fácil)
2. **Backup**: Guarda el Chat ID numérico por si cambias el username
3. **Permisos**: Solo da permisos necesarios al bot (seguridad)
4. **Pruebas**: Prueba siempre antes de usar en producción

---

¿Necesitas ayuda? Revisa:
- `docs/obtener-chat-id-sin-bots.md` - Cómo obtener Chat IDs
- `docs/checklist-configuracion.md` - Checklist completo de configuración



