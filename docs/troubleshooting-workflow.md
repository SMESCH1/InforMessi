# Troubleshooting del Workflow - InforMessi

Guía para diagnosticar problemas con el workflow de GitHub Actions.

## 🔍 Problemas Comunes

### 1. El workflow no envía mensajes a Telegram

**Síntomas:**
- El workflow se ejecuta pero no recibes mensajes
- Los logs muestran "Error al enviar, continuando..."

**Diagnóstico:**

1. **Verifica GitHub Secrets:**
   - Ve a tu repo → **Settings** → **Secrets and variables** → **Actions**
   - Verifica que estos secrets existan:
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_PREVIEW_CHAT_ID`
     - `TELEGRAM_PUBLIC_CHAT_ID`
   - **Importante**: Los valores deben ser exactos, sin espacios al inicio/final

2. **Verifica formato de Chat IDs:**
   - Grupos: deben ser negativos (ej: `-1001234567890`)
   - Chats privados: deben ser positivos (ej: `123456789`)
   - Sin comillas, sin espacios

3. **Ejecuta diagnóstico local:**
   ```bash
   python3 scripts/diagnose-workflow.py
   ```

4. **Revisa logs del workflow:**
   - Ve a GitHub → **Actions**
   - Click en el último workflow ejecutado
   - Revisa el step "Diagnóstico de configuración"
   - Revisa el step "Enviar a revisión en Telegram"

### 2. Error "chat not found"

**Causa**: El bot no está en el grupo o el Chat ID es incorrecto.

**Solución:**
1. Verifica que el bot esté agregado al grupo
2. Verifica el Chat ID usando:
   ```bash
   python3 scripts/get-chat-id-from-url.py
   ```
3. Actualiza el Chat ID en GitHub Secrets

### 3. Error "not enough rights"

**Causa**: El bot no tiene permisos para enviar mensajes.

**Solución:**
1. Ve al grupo en Telegram
2. Configuración del grupo → Administradores
3. Verifica que el bot pueda enviar mensajes
4. No necesita ser administrador, solo poder enviar

### 4. El informe no existe

**Síntomas:**
- Error: "Informe para YYYY-MM-DD no encontrado"

**Solución:**
1. Genera informes con antelación:
   ```bash
   python3 scripts/generate-advance-reports.py --days 15
   ```
2. Commit y push los informes:
   ```bash
   git add reports/
   git commit -m "Generar informes con antelación"
   git push
   ```

### 5. Variables de entorno no se cargan

**Síntomas:**
- Error: "Variables de Telegram no configuradas"

**Solución:**
1. Verifica que los secrets estén configurados en GitHub
2. Verifica que los nombres sean exactos (mayúsculas/minúsculas)
3. No uses espacios en los valores

### 6. El paso "Commit y push" falla

**Síntomas:**
- El job de GitHub Actions falla en el step "Commit y push cambios"
- Error de permisos o red al hacer `git push`

**Comportamiento:** Si el push falla, el job falla a propósito (ya no se usa `|| true`). Así se hace visible el problema. El siguiente run del workflow partirá del último commit exitoso: no tendrá los `reports/` ni `data/memory-database.json` del día, por lo que la memoria en CI puede quedar desactualizada hasta que el push vuelva a funcionar.

**Solución:**
1. Revisa que el token/workflow tenga permisos de escritura en el repo (Settings → Actions → General → Workflow permissions: Read and write).
2. Si usas branch protection, permite que el workflow haga push a `main` o usa un token con permisos suficientes.
3. Tras corregir, el siguiente run hará commit y push de los cambios pendientes.

### 7. El scraper diario no aparece en GitHub Actions (404) o no corre

**Síntomas:**

- `gh run list --workflow daily-news-scraper.yml` responde que el workflow no está en la rama por defecto.
- En el repo remoto solo existe `.github/workflows/daily-informessi.yml` (se puede comprobar con la API: `contents/.github/workflows`).

**Causa:** el archivo [`.github/workflows/daily-news-scraper.yml`](../.github/workflows/daily-news-scraper.yml) y el script [`scripts/scrape-daily-news.py`](../scripts/scrape-daily-news.py) **no están mergeados/pusheados** en `main` (o la rama default). GitHub solo ejecuta workflows presentes en esa rama.

**Qué hacer:**

1. Asegurate de tener en `main` (y pusheados) al menos: `daily-news-scraper.yml`, `scripts/scrape-daily-news.py`, y que [`scripts/collect-daily-data.py`](../scripts/collect-daily-data.py) lea `data/daily-news/<fecha>.json` si existe.
2. Creá el directorio rastreado `data/daily-news/` (p. ej. con `.gitkeep`) para que el primer commit del scraper sea claro.
3. En **Settings → Actions → General → Workflow permissions**, dejá **Read and write** (o el workflow debe declarar `permissions: contents: write` para poder hacer `git push`).
4. Secrets recomendados para el job (ya mapeados en el workflow):
   - `NEWSAPI_KEY` (opcional pero recomendado; sin él el fetch sigue con RSS/scraping según [`scripts/fetch-news.py`](../scripts/fetch-news.py)).
   - `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` (opcionales).
5. Tras el push, verificá: `gh workflow list` debe listar **InforMessi - Scraper de Noticias Diario**. Probar con **Actions → Run workflow** o `gh workflow run "InforMessi - Scraper de Noticias Diario.yml"`.
6. Éxito: aparece un commit con archivos bajo `data/daily-news/` (p. ej. `YYYY-MM-DD.json`).

**Prevención:** no asumir que un workflow local corre en CI hasta verlo en la rama default del remoto; usar `gh workflow list` o la pestaña Actions tras cada cambio de workflow.

## 🧪 Diagnóstico Paso a Paso

### Paso 1: Verificar Secrets en GitHub

1. Ve a tu repo → **Settings** → **Secrets and variables** → **Actions**
2. Verifica que existan:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_PREVIEW_CHAT_ID`
   - `TELEGRAM_PUBLIC_CHAT_ID`

### Paso 2: Probar Localmente

```bash
# Cargar variables de entorno
export TELEGRAM_BOT_TOKEN="tu_token"
export TELEGRAM_PREVIEW_CHAT_ID="tu_chat_id"
export TELEGRAM_PUBLIC_CHAT_ID="tu_grupo_id"

# Ejecutar diagnóstico
python3 scripts/diagnose-workflow.py

# Probar envío
python3 scripts/send-daily-report-review.py
```

### Paso 3: Revisar Logs del Workflow

1. Ve a GitHub → **Actions**
2. Click en el último workflow ejecutado
3. Revisa cada step:
   - **Diagnóstico de configuración**: Muestra errores de configuración
   - **Enviar a revisión en Telegram**: Muestra errores de envío

### Paso 4: Verificar Permisos del Bot

1. Abre Telegram
2. Ve al grupo/canal
3. Verifica que el bot esté agregado
4. Verifica permisos del bot

## 📋 Checklist de Verificación

- [ ] Secrets configurados en GitHub
- [ ] Chat IDs correctos (formato y valor)
- [ ] Bot agregado al grupo/canal
- [ ] Bot tiene permisos para enviar mensajes
- [ ] Informes generados en `reports/`
- [ ] Workflow ejecutado manualmente para probar
- [ ] Logs del workflow revisados

## 🔧 Comandos Útiles

```bash
# Diagnóstico completo
python3 scripts/diagnose-workflow.py

# Verificar Chat IDs actuales
python3 scripts/update-chat-ids.py --show-current

# Probar envío local
python3 scripts/send-daily-report-review.py

# Generar informes
python3 scripts/generate-advance-reports.py --days 15
```

## 💡 Tips

- **Siempre prueba localmente primero** antes de confiar en el workflow
- **Revisa los logs** del workflow en GitHub Actions
- **Usa el diagnóstico** para identificar problemas rápidamente
- **Actualiza los Chat IDs** si cambian los grupos

---

**Si el problema persiste, revisa los logs completos del workflow en GitHub Actions.**






