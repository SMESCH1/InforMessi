# Configuración de Telegram - Dos Chats Separados

Guía para configurar el sistema con chat de revisión privado y grupo público.

## 🎯 Arquitectura

```
┌─────────────────────┐
│  Generación/        │
│  Actualización      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Chat de Revisión   │  ← Solo tú ves esto
│  (Privado)          │     (Aprobar/Rechazar/Editar)
└──────────┬──────────┘
           │
           │ Si apruebas
           ▼
┌─────────────────────┐
│  Grupo Público      │  ← Todos ven esto
│  (Público)           │     (Solo mensajes aprobados)
└─────────────────────┘
```

**Flujo:**
1. El sistema envía el informe al **chat de revisión** (privado, solo tú)
2. Tú revisas y apruebas/rechazas/editas
3. Si apruebas, se publica en el **grupo público** (todos lo ven)

---

## 🔧 Configuración

### Paso 1: Crear Chat de Revisión (Privado)

**Opción A: Chat privado contigo mismo**

1. Abre Telegram
2. Busca tu bot (el que creaste para InforMessi)
3. Inicia una conversación con el bot
4. Envía cualquier mensaje (ej: `/start`)
5. Obtén el Chat ID:
   ```bash
   python3 scripts/get-telegram-chat-id.py
   ```
   O visita: `https://api.telegram.org/botTU_TOKEN/getUpdates`
   - Busca `"chat":{"id":123456789}` en la respuesta
   - Ese número es tu `TELEGRAM_PREVIEW_CHAT_ID`

**Opción B: Grupo privado (solo tú y el bot)**

1. Crea un grupo nuevo en Telegram
2. Agrega solo a tu bot
3. Obtén el Chat ID del grupo (mismo método que arriba)
4. Este será tu `TELEGRAM_PREVIEW_CHAT_ID`

---

### Paso 2: Crear Grupo Público

1. Crea un grupo en Telegram (o usa uno existente)
2. Agrega tu bot al grupo
3. **Importante:** Dale permisos de administrador al bot (opcional pero recomendado)
4. Obtén el Chat ID del grupo:
   ```bash
   python3 scripts/get-telegram-chat-id.py
   ```
   O envía un mensaje al grupo y revisa:
   `https://api.telegram.org/botTU_TOKEN/getUpdates`
   - Busca el ID del grupo (será negativo, ej: `-1001234567890`)
   - Ese número es tu `TELEGRAM_PUBLIC_CHAT_ID`

---

### Paso 3: Configurar Variables de Entorno

Agrega a tu `.env`:

```env
# Bot de Telegram
TELEGRAM_BOT_TOKEN=tu_token_del_bot

# Chat de revisión (privado, solo tú)
TELEGRAM_PREVIEW_CHAT_ID=123456789

# Grupo público (donde se publica después de aprobar)
TELEGRAM_PUBLIC_CHAT_ID=-1001234567890
```

**⚠️ IMPORTANTE:**
- `TELEGRAM_PREVIEW_CHAT_ID`: Chat privado (solo tú)
- `TELEGRAM_PUBLIC_CHAT_ID`: Grupo público (todos)

---

## 🧪 Probar Configuración

### Prueba Completa

```bash
# Probar ambos chats
python3 scripts/test-telegram.py

# Solo chat de revisión
python3 scripts/test-telegram.py --review-only

# Solo grupo público
python3 scripts/test-telegram.py --public-only

# Con prueba de foto
python3 scripts/test-telegram.py --with-photo
```

---

## 🚀 Uso Diario

### Flujo Automático (GitHub Actions)

1. **GitHub Actions ejecuta diariamente:**
   - Actualiza el informe del día
   - **NO envía automáticamente** (requiere aprobación manual)

### Flujo Manual

1. **Enviar a revisión:**
   ```bash
   python3 scripts/send-daily-report-review.py --date 2025-12-28
   ```
   - Se envía al chat privado de revisión
   - Solo tú lo ves
   - Aparecen botones: ✅ Aprobar, ❌ Rechazar, ✏️ Editar

2. **Revisar en Telegram:**
   - Abre tu chat privado con el bot
   - Revisa el mensaje
   - Usa los botones para aprobar/rechazar/editar

3. **Si apruebas, publicar:**
   ```bash
   python3 scripts/publish-approved-report.py --date 2025-12-28
   ```
   - Se publica en el grupo público
   - Todos los miembros del grupo lo ven

---

## 📋 Scripts Disponibles

### `send-daily-report-review.py`
Envía el informe al chat de revisión (privado).

```bash
python3 scripts/send-daily-report-review.py --date 2025-12-28
```

### `publish-approved-report.py`
Publica un informe aprobado al grupo público.

```bash
python3 scripts/publish-approved-report.py --date 2025-12-28
```

### `test-telegram.py`
Prueba la configuración de ambos chats.

```bash
python3 scripts/test-telegram.py
```

---

## 🔒 Seguridad y Privacidad

### Chat de Revisión (Privado)

- ✅ Solo tú tienes acceso
- ✅ El bot puede enviar mensajes
- ✅ Los botones de aprobación solo funcionan para ti
- ✅ Nadie más ve este chat

### Grupo Público

- ✅ Solo se publica después de tu aprobación
- ✅ El bot publica directamente (no aparece como "enviado por bot")
- ✅ Los miembros del grupo solo ven mensajes aprobados
- ✅ No ven el proceso de revisión

---

## 💡 Tips

1. **Chat de revisión:**
   - Úsalo como tu "bandeja de entrada" de informes
   - Revisa y aprueba cuando tengas tiempo
   - Puedes editar el informe antes de aprobar

2. **Grupo público:**
   - Solo contiene mensajes aprobados
   - Los miembros confían en que todo está revisado
   - Mantiene la calidad del contenido

3. **Automatización:**
   - GitHub Actions actualiza el informe diariamente
   - Tú decides cuándo enviar a revisión
   - Tú decides cuándo publicar

---

## 🐛 Troubleshooting

### El bot no envía al chat de revisión

1. Verifica que el bot esté iniciado:
   ```bash
   python3 scripts/test-telegram.py --review-only
   ```

2. Verifica el Chat ID:
   - Debe ser un número positivo (chat privado)
   - Obtén el ID correcto con `get-telegram-chat-id.py`

### El bot no envía al grupo público

1. Verifica que el bot esté en el grupo
2. Verifica que tenga permisos para enviar mensajes
3. Verifica el Chat ID:
   - Debe ser un número negativo (grupo)
   - Ejemplo: `-1001234567890`

### Los botones no funcionan

- Los botones solo funcionan en el chat de revisión
- Debes hacer click en los botones en tu chat privado
- Si no funcionan, usa `publish-approved-report.py` manualmente

---

*Última actualización: 2025-12-28*

