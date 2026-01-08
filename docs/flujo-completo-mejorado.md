# Flujo Completo Mejorado - InforMessi

## 📋 Resumen

El sistema ahora soporta:
1. **Generación anticipada** de informes
2. **Edición y validación previa** (sin pasar por preview)
3. **Validación en preview** (si no está pre-aprobado)
4. **Publicación automática** según el estado

## 🔄 Flujos de Trabajo

### Flujo 1: Generación Anticipada + Validación Previa

1. **Generar informes con anticipación:**
   ```bash
   python3 scripts/generate-advance-reports.py --days 15
   ```

2. **Editar y validar informes:**
   ```bash
   python3 scripts/edit-and-validate-report.py --date 2025-12-29
   ```
   
   Opciones:
   - **Editar mensaje**: Permite modificar el contenido
   - **Validar sin editar**: Marca como pre-aprobado
   - **Cancelar**: No hace cambios

3. **Resultado:**
   - Si está `pre_approved: true`, se publica directamente sin preview
   - Si no está pre-aprobado, pasa por preview normal

### Flujo 2: Validación en Preview (Automático)

1. **GitHub Actions** ejecuta diariamente a las 10:15 AM (Argentina):
   - Genera informe si no existe
   - Actualiza con datos recientes
   - Envía a preview (si no está pre-aprobado)

2. **Usuario recibe mensaje en chat privado** con botones:
   - ✅ **Aprobar**: Publica directamente en grupo público
   - ❌ **Rechazar**: No publica
   - ✏️ **Editar**: Permite enviar versión editada

3. **Si no hay respuesta en 2 horas:**
   - Se publica automáticamente (fallback)

### Flujo 3: Edición desde Preview

1. Usuario hace clic en **✏️ Editar**
2. Bot pide enviar mensaje editado
3. Usuario envía mensaje corregido al bot
4. Bot actualiza el informe y publica automáticamente

## 📊 Estados de Informe

```json
{
  "date": "2025-12-29",
  "status": "draft|updated|published",
  "pre_approved": false,
  "pre_approved_at": null,
  "published_at": null
}
```

**Estados:**
- `draft`: Generado pero no actualizado
- `updated`: Actualizado con datos recientes
- `published`: Ya publicado en Telegram

**Pre-aprobación:**
- `pre_approved: true`: Se publica directamente sin preview
- `pre_approved: false`: Requiere validación en preview

## 🛠️ Scripts Principales

### `generate-advance-reports.py`
Genera informes con antelación.

```bash
python3 scripts/generate-advance-reports.py --days 15
```

### `edit-and-validate-report.py`
Edita y valida informes anticipadamente.

```bash
python3 scripts/edit-and-validate-report.py --date 2025-12-29
```

### `update-today-report.py`
Actualiza el informe del día con datos recientes.

```bash
python3 scripts/update-today-report.py
```

### `send-daily-report-review.py`
Envía el informe a preview (o publica directamente si está pre-aprobado).

```bash
python3 scripts/send-daily-report-review.py
```

## 🔧 Configuración

### Variables de Entorno Requeridas

```env
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_PREVIEW_CHAT_ID=tu_chat_privado
TELEGRAM_PUBLIC_CHAT_ID=tu_grupo_publico
```

### GitHub Secrets

Configurar en: Settings → Secrets and variables → Actions

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_PREVIEW_CHAT_ID`
- `TELEGRAM_PUBLIC_CHAT_ID`
- `NEWSAPI_KEY`
- `OPENWEATHER_API_KEY`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`

### Render (Webhook Server)

Configurar en: Environment Variables

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_PREVIEW_CHAT_ID`
- `TELEGRAM_PUBLIC_CHAT_ID`

## 📝 Ejemplo de Uso

### Caso 1: Validar informes de la semana

```bash
# Generar informes para la próxima semana
python3 scripts/generate-advance-reports.py --days 7

# Editar y validar cada uno
python3 scripts/edit-and-validate-report.py --date 2025-12-29
python3 scripts/edit-and-validate-report.py --date 2025-12-30
# ... etc
```

### Caso 2: Dejar que funcione automáticamente

1. GitHub Actions genera y actualiza diariamente
2. Si no está pre-aprobado, envía a preview
3. Usuario aprueba/rechaza/edita desde Telegram
4. Si no hay respuesta, se publica automáticamente

## ⚠️ Notas Importantes

1. **Pre-aprobación**: Si un informe está `pre_approved: true`, se publica directamente sin pasar por preview.

2. **Actualización**: El workflow actualiza el informe del día con datos recientes, pero mantiene `pre_approved` si ya estaba configurado.

3. **Webhook**: El servidor webhook en Render procesa las aprobaciones/ediciones automáticamente.

4. **Fallback**: Si no hay aprobación en 2 horas, se publica automáticamente.

## 🐛 Troubleshooting

### El informe no se publica automáticamente

1. Verificar que `pre_approved: true` en el informe
2. Verificar que `TELEGRAM_PUBLIC_CHAT_ID` esté configurado
3. Verificar que el bot esté en el grupo público
4. Revisar logs de GitHub Actions

### El webhook no funciona

1. Verificar que el webhook esté configurado:
   ```bash
   python3 scripts/setup-webhook.py --info
   ```

2. Verificar que Render esté activo:
   ```bash
   curl https://tu-webhook-url.onrender.com/health
   ```

3. Revisar logs de Render

### El informe no se genera

1. Verificar que Ollama esté disponible (para generación local)
2. Verificar que las APIs estén configuradas (NewsAPI, Reddit, etc.)
3. Revisar logs de errores




