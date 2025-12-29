# Flujo Automático con Aprobación Manual - InforMessi

Esta guía explica cómo funciona el sistema cuando GitHub Actions ejecuta el flujo automáticamente y tu PC no está prendida.

## 🎯 Problema

Cuando GitHub Actions ejecuta el workflow:
- ✅ Puede actualizar el informe del día
- ✅ Puede enviar el mensaje a Telegram
- ❌ **NO puede esperar** tu aprobación (GitHub Actions tiene límites de tiempo)

## ✅ Solución: Flujo Asíncrono

El sistema funciona de forma **asíncrona**:

### 1. GitHub Actions (Automático)

```
8:00 AM UTC (diario)
    ↓
GitHub Actions ejecuta:
    ↓
1. Actualiza informe del día con datos recientes
2. Envía mensaje a Telegram (chat privado) con botones
3. Termina inmediatamente (NO espera)
    ↓
El mensaje queda en Telegram esperando tu revisión
```

**Script usado:** `send-daily-report-review.py` (con `--no-wait`)

### 2. Tú (Cuando Veas el Mensaje)

```
Recibes notificación en Telegram
    ↓
Abras Telegram (desde móvil o PC)
    ↓
Ves el mensaje con botones:
    ✅ Aprobar
    ❌ Rechazar
    ✏️ Editar
    ↓
Haces click en una opción
```

### 3. ¿Qué Pasa al Aprobar?

**⚠️ IMPORTANTE: Limitación Actual**

Cuando haces click en "✅ Aprobar" en Telegram:
- El bot recibe el callback
- **PERO** necesita que un script esté corriendo para procesarlo
- Si tu PC no está prendida, el callback se pierde

**Solución Actual (2 Opciones):**

**Opción A: Aprobación Manual (Recomendado para MVP)**

1. GitHub Actions envía el mensaje a Telegram
2. Tú ves el mensaje cuando puedas (desde móvil o PC)
3. Cuando tengas tu PC prendida:
   ```bash
   python3 scripts/publish-approved-report.py
   ```
4. El script publica el informe en el grupo público

**Opción B: Script con Espera (Solo si PC está prendida)**

Si tu PC está prendida cuando GitHub Actions ejecuta:

1. Usa `send-daily-report-review-wait.py` en lugar de `send-daily-report-review.py`
2. El script espera tu respuesta
3. Cuando haces click en "✅ Aprobar", se publica automáticamente

**⚠️ Limitación:** GitHub Actions no puede esperar indefinidamente, así que esta opción solo funciona si ejecutas el script manualmente desde tu PC.

**Opción B: Aprobación Manual**

Si NO configuraste `TELEGRAM_PUBLIC_CHAT_ID` o prefieres publicar manualmente:

1. Haces click en "✅ Aprobar" en Telegram
2. El bot te indica que debes publicar manualmente
3. Cuando tengas tu PC prendida:
   ```bash
   python3 scripts/publish-approved-report.py
   ```

## 📱 Flujo Completo Visual

```
┌─────────────────────────────────────┐
│  GitHub Actions (8:00 AM UTC)      │
│  - Actualiza informe                │
│  - Envía a Telegram (--no-wait)     │
│  - Termina                          │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Telegram (Chat Privado)            │
│  - Mensaje con botones              │
│  - Esperando tu revisión            │
└──────────────┬──────────────────────┘
               │
               ↓ (Cuando veas el mensaje)
┌─────────────────────────────────────┐
│  Tú (desde móvil o PC)              │
│  - Revisas el mensaje               │
│  - Click en ✅ Aprobar              │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Bot de Telegram (Automático)       │
│  - Detecta aprobación               │
│  - Publica en grupo público          │
│  ✅ SIN NECESIDAD DE TU PC          │
└─────────────────────────────────────┘
```

## 🔧 Configuración Requerida

Para que la aprobación automática funcione:

### 1. Secrets de GitHub Actions

Asegúrate de tener configurado en GitHub → Settings → Secrets:

```
TELEGRAM_BOT_TOKEN
TELEGRAM_PREVIEW_CHAT_ID
TELEGRAM_PUBLIC_CHAT_ID  ← IMPORTANTE para aprobación automática
```

### 2. Verificar en `telegram-preview.py`

El script debe estar configurado para publicar automáticamente cuando se aprueba:

```python
# En telegram-preview.py, cuando response == "approve":
public_chat_id = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
if public_chat_id:
    publish_message(bot, public_chat_id, args.message)
```

✅ Esto ya está implementado en el código actual.

## ⏰ Ventajas del Flujo Asíncrono

1. **No necesitas PC prendida**: GitHub Actions hace el trabajo pesado
2. **Revisas cuando puedas**: El mensaje queda en Telegram esperando
3. **Aprobación desde móvil**: Puedes aprobar desde tu teléfono
4. **Publicación automática**: Si configuraste `TELEGRAM_PUBLIC_CHAT_ID`, se publica automáticamente

## 🧪 Probar el Flujo

### Simular GitHub Actions Localmente

```bash
# 1. Actualizar informe
python3 scripts/update-today-report.py

# 2. Enviar a Telegram (sin esperar)
python3 scripts/send-daily-report-review.py
# Este script usa --no-wait, termina inmediatamente

# 3. Revisar en Telegram
# - Abre Telegram
# - Ve al chat privado
# - Haz click en ✅ Aprobar
# - Se publicará automáticamente en el grupo público
```

### Verificar que Funciona

1. Ejecuta `send-daily-report-review.py`
2. Verifica que el mensaje llegue a Telegram
3. Haz click en "✅ Aprobar"
4. Verifica que se publique en el grupo público

## ⚠️ Limitaciones Actuales

1. **Edición**: Si haces click en "✏️ Editar", necesitas tener la PC para editar el archivo JSON
   - **Solución futura**: Integrar con Notion o webhook para edición desde móvil

2. **Timeout de GitHub Actions**: Si el workflow tarda más de 6 horas, falla
   - **No es problema**: El workflow actual termina en segundos

3. **Ollama no disponible en GitHub Actions**: No se puede generar mensajes nuevos
   - **Solución actual**: Generas mensajes anticipadamente localmente
   - **Solución futura**: Usar API de LLM (OpenAI, Anthropic, etc.)

## 📚 Referencias

- [Configuración de GitHub Actions](github-actions-setup.md)
- [Flujo de Revisión Humana](human-review-flow.md)
- [Configuración de Telegram](configuracion-telegram-dos-chats.md)

