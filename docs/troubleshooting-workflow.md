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






