# Configuración de GitHub Actions - InforMessi

Guía para configurar GitHub Actions para ejecución diaria automática.

## 🎯 Objetivo

Configurar GitHub Actions para que:
- Actualice el informe del día automáticamente
- Haga commit y push de los cambios
- **NO publique automáticamente** (requiere aprobación manual)

---

## 🔧 Configuración

### Paso 1: Agregar Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Agrega los siguientes secrets:

**Secrets Requeridos:**

```
TELEGRAM_BOT_TOKEN
TELEGRAM_PREVIEW_CHAT_ID
TELEGRAM_PUBLIC_CHAT_ID
GROQ_API_KEY
NEWSAPI_KEY
REDDIT_CLIENT_ID (opcional)
REDDIT_CLIENT_SECRET (opcional)
REDDIT_USER_AGENT (opcional)
```

**Cómo obtener cada valor:**

- `TELEGRAM_BOT_TOKEN`: Token de tu bot (de @BotFather)
- `TELEGRAM_PREVIEW_CHAT_ID`: Chat ID del chat privado de revisión
- `TELEGRAM_PUBLIC_CHAT_ID`: Chat ID del grupo público
- `GROQ_API_KEY`: API key de Groq (para LLM en CI)
- `NEWSAPI_KEY`: Tu API key de NewsAPI
- `REDDIT_*`: Credenciales de Reddit (opcional)

---

### Paso 2: Obtener Chat IDs de Telegram

```bash
# Ejecutar script para obtener Chat IDs
python3 scripts/get-telegram-chat-id.py
```

**Instrucciones:**
1. Asegúrate de que el bot esté agregado a ambos chats
2. Envía un mensaje en cada chat
3. Ejecuta el script
4. Copia los Chat IDs que aparecen

**Tipos de Chat ID:**
- **Chat privado**: Número positivo (ej: `123456789`)
- **Grupo/Canal**: Número negativo (ej: `-1001234567890`)

---

### Paso 3: Verificar Workflow

El workflow está en: `.github/workflows/daily-informessi.yml`

**Horario:**
- Se ejecuta diariamente a las **8:00 AM UTC** (5:00 AM Argentina)
- También se puede ejecutar manualmente desde GitHub Actions

**Qué hace:**
1. Actualiza el informe del día con datos recientes
2. Hace commit y push de los cambios
3. **NO envía a Telegram automáticamente** (requiere acción manual)

---

## 🧪 Probar Workflow

### Ejecución Manual

1. Ve a tu repositorio en GitHub
2. Actions → "InforMessi - Flujo Diario Completo"
3. Click "Run workflow"
4. Selecciona la rama (ej: `mvp-v1-generacion-anticipada`)
5. Click "Run workflow"

### Ver Logs

1. Ve a Actions
2. Click en el workflow ejecutado
3. Click en el job "update-and-send-report"
4. Revisa los logs de cada step

---

## 📋 Flujo Completo con GitHub Actions

### Automático (GitHub Actions)

```
8:00 AM UTC (diario)
    ↓
GitHub Actions ejecuta:
    ↓
1. Actualiza informe del día
2. Commit y push cambios
    ↓
Espera aprobación manual
```

### Manual (Tú)

```
1. Revisar cambios en GitHub
    ↓
2. Enviar a revisión:
   python3 scripts/send-daily-report-review.py
    ↓
3. Revisar en Telegram (chat privado)
    ↓
4. Si apruebas:
   python3 scripts/publish-approved-report.py
    ↓
5. Se publica en grupo público
```

---

## ⚙️ Configuración Avanzada

### Cambiar Horario

Edita `.github/workflows/daily-informessi.yml`:

```yaml
schedule:
  - cron: '0 8 * * *'  # 8:00 AM UTC
```

**Ejemplos:**
- `'0 10 * * *'` - 10:00 AM UTC (7:00 AM Argentina)
- `'0 12 * * *'` - 12:00 PM UTC (9:00 AM Argentina)

### Agregar Notificación

Puedes agregar un step para notificar en Telegram cuando el workflow termine:

```yaml
- name: Notificar en Telegram
  run: |
    python3 scripts/notify-telegram.py \
      --message "Workflow completado: $(date +%Y-%m-%d)"
```

---

## 🐛 Troubleshooting

### El workflow falla

1. **Revisa los logs:**
   - Ve a Actions → Workflow ejecutado → Ver logs

2. **Verifica secrets:**
   - Asegúrate de que todos los secrets estén configurados
   - Verifica que los valores sean correctos

3. **Verifica permisos:**
   - El workflow necesita permisos de escritura para hacer push
   - Settings → Actions → General → Workflow permissions → "Read and write permissions"

### No se actualiza el informe

1. **Verifica que el informe exista:**
   - Debe haber un informe en `reports/YYYY-MM-DD.json`
   - Si no existe, genera uno primero: `python3 scripts/generate-advance-reports.py`

2. **Verifica APIs:**
   - NewsAPI, Reddit, etc. deben estar funcionando
   - Revisa los logs del workflow

### No se hace commit

1. **Verifica permisos:**
   - El workflow necesita permisos de escritura
   - Settings → Actions → General → Workflow permissions

2. **Verifica que haya cambios:**
   - Si no hay cambios, no se hace commit (esto es normal)

---

## 💡 Tips

1. **Monitorea regularmente:**
   - Revisa los workflows ejecutados semanalmente
   - Verifica que se estén actualizando los informes

2. **Prueba manualmente primero:**
   - Antes de confiar en el workflow automático, ejecútalo manualmente
   - Verifica que todo funcione correctamente

3. **Mantén secrets actualizados:**
   - Si cambias alguna API key, actualiza el secret en GitHub

---

*Última actualización: 2025-12-28*

