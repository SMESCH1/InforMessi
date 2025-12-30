# Guía de Pruebas de Flujos Automáticos

## 🧪 Pruebas Automáticas

Ejecuta el script de pruebas para verificar que todo esté configurado:

```bash
python3 scripts/test-flujos-completos.py
```

Este script verifica:
- ✅ Cron de GitHub Actions configurado
- ✅ Fallback automático configurado
- ✅ Detección de informes pre-aprobados
- ✅ Flujo de generación/edición/pre-aprobación

## 🔄 Pruebas Manuales

### Prueba 1: Cron de GitHub Actions

1. Ve a GitHub → Actions → "InforMessi - Flujo Diario Completo"
2. Click en "Run workflow"
3. Selecciona la rama y ejecuta
4. Verifica que:
   - Se genera/actualiza el informe
   - Se envía a preview (si no está pre-aprobado)
   - Se ejecuta el fallback

**Nota:** El cron se ejecuta automáticamente todos los días a las 10:15 AM (Argentina).

### Prueba 2: Fallback Automático

El fallback publica automáticamente informes que no fueron aprobados después de 2 horas.

Para probar con un tiempo más corto:

```bash
# Publicar informes de hace 6 minutos sin respuesta
python3 scripts/auto-publish-fallback.py --check-all --hours 0.1
```

**En producción:** El workflow ejecuta esto automáticamente con `--hours 2`.

### Prueba 3: Informes Pre-Aprobados

1. **Generar informe:**
   ```bash
   python3 scripts/generate-advance-reports.py --days 1 --start-date 2025-12-31
   ```

2. **Editar y pre-aprobar:**
   ```bash
   python3 scripts/edit-and-validate-report.py --date 2025-12-31
   # Selecciona opción 2: "Validar sin editar"
   ```

3. **Enviar (debería publicar directamente):**
   ```bash
   python3 scripts/send-daily-report-review.py --date 2025-12-31
   ```

**Resultado esperado:** El informe se publica directamente en el grupo público sin pasar por preview.

### Prueba 4: Flujo Completo (Generación → Edición → Pre-Aprobación)

Ejecuta el script de pruebas manuales:

```bash
bash scripts/probar-flujos-manuales.sh
```

O manualmente:

```bash
# 1. Generar
python3 scripts/generate-advance-reports.py --days 1 --start-date 2025-12-31

# 2. Editar y pre-aprobar
python3 scripts/edit-and-validate-report.py --date 2025-12-31

# 3. Enviar (publicará directamente)
python3 scripts/send-daily-report-review.py --date 2025-12-31
```

## 📋 Checklist de Verificación

Antes de que funcione automáticamente mañana, verifica:

- [ ] **Cron configurado:** `15 13 * * *` en `.github/workflows/daily-informessi.yml`
- [ ] **Webhook configurado:** `python3 scripts/setup-webhook.py --info` muestra URL
- [ ] **Token válido:** `python3 scripts/verify-bot-token.py` muestra token válido
- [ ] **Fallback configurado:** Workflow incluye `auto-publish-fallback.py --hours 2`
- [ ] **Pre-aprobación funciona:** Prueba con un informe de prueba
- [ ] **Render activo:** `curl https://informessi-webhook.onrender.com/health` responde OK

## 🚀 Flujo Automático para Mañana

1. **10:15 AM (Argentina):** GitHub Actions ejecuta el workflow
2. **10:15 AM:** Se genera/actualiza el informe del día
3. **10:15 AM:** Se envía a preview (si no está pre-aprobado)
4. **Tú:** Recibes mensaje en chat privado con botones
5. **Tú:** Apruebas/rechazas/editas desde Telegram
6. **Automático:** Render procesa el callback y publica
7. **12:15 PM (2 horas después):** Si no respondiste, se publica automáticamente

## ⚠️ Si Algo No Funciona

### El workflow no se ejecuta automáticamente

1. Verifica que el cron esté correcto: `15 13 * * *`
2. Verifica que el workflow esté habilitado en GitHub
3. Ejecuta manualmente: Actions → Run workflow

### Los botones no funcionan

1. Verifica el webhook: `python3 scripts/setup-webhook.py --info`
2. Verifica que Render esté activo
3. Revisa los logs de Render cuando presionas un botón
4. Como backup, usa: `python3 scripts/send-and-wait-local.py`

### El fallback no publica

1. Verifica que el informe tenga `updated_at` reciente
2. Verifica que el informe NO tenga `published_at`
3. Ejecuta manualmente: `python3 scripts/auto-publish-fallback.py --check-all --hours 2`

### Los pre-aprobados no se publican directamente

1. Verifica que el informe tenga `pre_approved: true`
2. Verifica que `send-daily-report-review.py` detecte pre-aprobados
3. Revisa los logs al ejecutar el script

## 📝 Notas

- El fallback se ejecuta **2 horas después** de que se actualiza el informe
- Los informes pre-aprobados se publican **inmediatamente** sin preview
- El webhook requiere que Render esté activo (puede dormirse después de inactividad)
- Si Render está dormido, el primer callback lo despertará (puede tardar 30 segundos)

