# Actualizar Chat IDs de Telegram - InforMessi

Guía para actualizar los Chat IDs cuando cambian (por ejemplo, cuando un grupo se convierte en supergrupo).

## 🔍 ¿Por Qué Cambian los Chat IDs?

Los Chat IDs pueden cambiar cuando:
- Un grupo se convierte en **supergrupo** (migración)
- Se crea un nuevo grupo
- Se cambia la configuración del grupo

**Nota**: Cambiar el **nombre** del grupo NO cambia el Chat ID, pero la migración a supergrupo sí.

## 📋 Lugares Donde Actualizar

Los Chat IDs deben actualizarse en **3 lugares**:

1. **`.env` local** (para scripts locales)
2. **GitHub Secrets** (para GitHub Actions)
3. **Render** (para el webhook server)

## 🔧 Pasos para Actualizar

### Paso 1: Obtener los Nuevos Chat IDs

**Opción A: Desde la URL del Grupo (Más Rápido)**
1. Abre Telegram Desktop o Web
2. Ve al grupo/canal
3. Click derecho → "Copy link" o "Copiar enlace"
4. O desde el navegador, copia la URL completa
5. Usa el script: `python3 scripts/get-chat-id-from-url.py`

**Opción B: Eliminar Webhook Temporalmente**
```bash
# 1. Eliminar webhook
python3 scripts/setup-webhook.py --remove

# 2. Obtener Chat IDs
python3 scripts/get-telegram-chat-id.py

# 3. Restaurar webhook
python3 scripts/setup-webhook.py --webhook-url https://informessi-webhook.onrender.com
```

### Paso 2: Actualizar en .env Local

Usa el script automático:

```bash
python3 scripts/update-chat-ids.py \
  --preview-chat-id NUEVO_PREVIEW_ID \
  --public-chat-id NUEVO_PUBLIC_ID
```

O manualmente:
1. Abre `.env`
2. Busca `TELEGRAM_PREVIEW_CHAT_ID` y `TELEGRAM_PUBLIC_CHAT_ID`
3. Actualiza los valores

### Paso 3: Actualizar en GitHub Secrets

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Para cada Chat ID:
   - Click en el secret (ej: `TELEGRAM_PREVIEW_CHAT_ID`)
   - Click **Update**
   - Ingresa el nuevo valor
   - Click **Update secret**

**Chat IDs a actualizar:**
- `TELEGRAM_PREVIEW_CHAT_ID`
- `TELEGRAM_PUBLIC_CHAT_ID`

### Paso 4: Actualizar en Render

1. Ve a Render: https://dashboard.render.com
2. Selecciona tu servicio `informessi-webhook`
3. Click en **Environment** (menú lateral)
4. Para cada Chat ID:
   - Busca la variable (ej: `TELEGRAM_PUBLIC_CHAT_ID`)
   - Click en el valor
   - Edita con el nuevo Chat ID
   - Click **Save Changes**
5. Render reiniciará automáticamente el servicio

**Chat IDs a actualizar:**
- `TELEGRAM_PUBLIC_CHAT_ID` (el preview no se usa en Render)

## ✅ Verificar que Funciona

### Verificar .env Local

```bash
python3 scripts/update-chat-ids.py --show-current
```

### Verificar GitHub Secrets

1. Ve a **Settings** → **Secrets and variables** → **Actions**
2. Verifica que los valores sean correctos

### Verificar Render

1. Ve a Render → Tu servicio → **Environment**
2. Verifica que `TELEGRAM_PUBLIC_CHAT_ID` sea correcto

### Probar Publicación

```bash
# Probar publicación manual
python3 scripts/publish-approved-report.py
```

O prueba el flujo completo:
1. Ejecuta el workflow de GitHub Actions
2. Aproba desde Telegram
3. Verifica que se publique en el grupo público

## 🐛 Troubleshooting

### El Chat ID sigue sin funcionar

1. **Verifica que el bot esté en el grupo**:
   - Abre el grupo en Telegram
   - Verifica que el bot esté agregado

2. **Verifica permisos del bot**:
   - El bot debe poder enviar mensajes
   - No necesita ser administrador

3. **Verifica formato del Chat ID**:
   - Grupos: número negativo (ej: `-1001234567890`)
   - Chats privados: número positivo (ej: `123456789`)

4. **Reinicia el servicio en Render**:
   - Render → Tu servicio → **Manual Deploy** → **Deploy latest commit**

## 📝 Notas

- **Chat ID de grupos**: Siempre es negativo (ej: `-1001234567890`)
- **Chat ID de chats privados**: Siempre es positivo (ej: `123456789`)
- **No incluyas espacios** al copiar el Chat ID
- **Render reinicia automáticamente** cuando cambias variables de entorno

---

**Una vez actualizados los 3 lugares, el sistema debería funcionar correctamente.**

