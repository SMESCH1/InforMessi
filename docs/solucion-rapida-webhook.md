# Solución Rápida: Webhook No Funciona

## 🔴 Problema
- El webhook no está configurado en Telegram (URL vacía)
- Los botones de aprobar/rechazar/editar no funcionan
- Render está activo pero no recibe callbacks

## ✅ Solución RÁPIDA (5 minutos)

### Paso 1: Configurar Webhook en Telegram

```bash
python3 scripts/setup-webhook.py --webhook-url https://informessi-webhook.onrender.com
```

Esto configurará el webhook para que Telegram envíe los callbacks a Render.

### Paso 2: Verificar que Funcione

```bash
python3 scripts/setup-webhook.py --info
```

Debería mostrar la URL del webhook configurada.

### Paso 3: Probar

1. Ejecuta: `python3 scripts/send-daily-report-review.py`
2. Haz clic en "Aprobar" en Telegram
3. Revisa los logs de Render para ver si recibe el callback

## 🔄 Alternativa: Script Local (Si Webhook No Funciona)

Si el webhook sigue sin funcionar, usa el script local que espera la respuesta:

```bash
python3 scripts/send-and-wait-local.py
```

Este script:
- Envía el mensaje a preview
- Espera localmente que presiones los botones
- Procesa la respuesta y publica automáticamente

**Limitación:** Requiere que tu PC esté prendida y el script corriendo.

## 📋 Para Mañana (Automático)

### Opción A: Webhook Funcionando (RECOMENDADO)

1. Configura el webhook hoy: `python3 scripts/setup-webhook.py --webhook-url https://informessi-webhook.onrender.com`
2. El workflow de GitHub Actions enviará a preview
3. Tú apruebas desde Telegram
4. Render procesa automáticamente y publica

### Opción B: Pre-aprobar Informes

1. Genera informes con anticipación:
   ```bash
   python3 scripts/generate-advance-reports.py --days 7
   ```

2. Edita y valida cada uno:
   ```bash
   python3 scripts/edit-and-validate-report.py --date 2025-12-31
   # Selecciona opción 2: "Validar sin editar"
   ```

3. Los informes pre-aprobados se publican automáticamente sin preview

## 🚀 Flujo Recomendado para Mañana

1. **Hoy (5 min):** Configura el webhook
2. **Mañana:** El workflow se ejecuta automáticamente
3. **Tú:** Recibes mensaje en preview, apruebas desde Telegram
4. **Automático:** Se publica en grupo público

## ⚠️ Si el Webhook Sigue Sin Funcionar

1. Verifica que Render esté activo: `curl https://informessi-webhook.onrender.com/health`
2. Verifica el token en Render (debe ser el mismo que en .env)
3. Revisa los logs de Render cuando presionas un botón
4. Como último recurso, usa el script local: `send-and-wait-local.py`




