# Flujo Completo - InforMessi

Este documento explica el flujo completo del sistema InforMessi desde la recolección de datos hasta la publicación.

## 📋 Flujo Completo

```
1. Recolección de Datos
   ↓
2. Generación de Mensaje (con secciones semanales)
   ↓
3. Revisión Humana (Telegram)
   ↓
4. Publicación
```

---

## 🔄 Paso a Paso

### 1. Recolección de Datos (`collect-daily-data.py`)

**Qué hace**:
- Obtiene eventos del día (desde `events.json` + Wikipedia + calendario)
- Obtiene noticias (NewsAPI + RSS + scraping)
- Calcula días restantes al Mundial
- Determina sección semanal según el día

**Comando**:
```bash
source venv/bin/activate
export $(grep -v '^#' .env | grep -v '^$' | xargs)

python3 scripts/collect-daily-data.py \
  --date 2025-12-22 \
  --output /tmp/datos-hoy.json
```

**Salida**: Archivo JSON con todos los datos del día

---

### 2. Generación de Mensaje (`generate-message.py`)

**Qué hace**:
- Carga prompts (system + main + sección semanal)
- Construye prompt completo con datos del día
- Llama al LLM (Ollama) para generar mensaje
- Valida longitud y estructura

**Comando**:
```bash
python3 scripts/generate-message.py \
  --data /tmp/datos-hoy.json \
  --output /tmp/mensaje.txt
```

**Salida**: Mensaje generado listo para revisar

---

### 3. Revisión Humana (`telegram-preview.py`)

**Qué hace**:
- Envía preview del mensaje a Telegram
- Espera aprobación/rechazo/edición
- Publica en canal público si se aprueba

**Comando**:
```bash
python3 scripts/telegram-preview.py \
  --message "$(cat /tmp/mensaje.txt)" \
  --preview-chat-id $TELEGRAM_PREVIEW_CHAT_ID \
  --token $TELEGRAM_BOT_TOKEN
```

**Salida**: Mensaje publicado o rechazado

---

## 🚀 Flujo Automatizado (Script Completo)

### Script de Flujo Completo

```bash
#!/bin/bash
# scripts/daily-flow.sh

source venv/bin/activate
export $(grep -v '^#' .env | grep -v '^$' | xargs)

DATE=$(date +"%Y-%m-%d")
DATA_FILE="/tmp/datos-${DATE}.json"
MESSAGE_FILE="/tmp/mensaje-${DATE}.txt"

echo "📊 Paso 1: Recolectando datos..."
python3 scripts/collect-daily-data.py \
  --date "$DATE" \
  --output "$DATA_FILE"

echo ""
echo "📝 Paso 2: Generando mensaje..."
python3 scripts/generate-message.py \
  --data "$DATA_FILE" \
  --output "$MESSAGE_FILE"

echo ""
echo "📤 Paso 3: Enviando para revisión..."
python3 scripts/telegram-preview.py \
  --message "$(cat $MESSAGE_FILE)" \
  --preview-chat-id $TELEGRAM_PREVIEW_CHAT_ID \
  --token $TELEGRAM_BOT_TOKEN

echo ""
echo "✅ Flujo completo finalizado"
```

---

## 📅 Secciones Semanales Automáticas

El sistema detecta automáticamente el día de la semana y agrega la sección correspondiente:

- **Lunes/Viernes**: Selección Argentina en Mundiales
- **Martes/Jueves**: Jugador de la Scaloneta
- **Sábado**: Dato Mundialista
- **Domingo**: Dato del País Sede
- **Miércoles**: Formato estándar

**No requiere configuración**, se aplica automáticamente.

---

## 📦 Eventos Históricos de Wikipedia

### Scrapear Eventos

```bash
# Scrapear todos los meses (una vez)
python3 scripts/scrape-wikipedia-events.py --merge

# O scrapear mes por mes
python3 scripts/scrape-wikipedia-events.py --month 12 --merge
```

### Verificar Eventos

```bash
# Ver eventos para una fecha específica
python3 scripts/fetch-events-enhanced.py --date 2026-12-22
```

Los eventos scrapeados se guardan en `data/events.json` y se verifican automáticamente cada día.

---

## 🧪 Prueba Completa

```bash
source venv/bin/activate
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# 1. Recolectar
python3 scripts/collect-daily-data.py --output /tmp/test-datos.json

# 2. Generar
python3 scripts/generate-message.py --data /tmp/test-datos.json --output /tmp/test-mensaje.txt

# 3. Ver resultado
cat /tmp/test-mensaje.txt

# 4. (Opcional) Enviar para revisión
python3 scripts/telegram-preview.py \
  --message "$(cat /tmp/test-mensaje.txt)" \
  --preview-chat-id $TELEGRAM_PREVIEW_CHAT_ID \
  --token $TELEGRAM_BOT_TOKEN
```

---

## 🔄 Automatización con Cron

Para ejecutar automáticamente cada día:

```bash
# Editar crontab
crontab -e

# Agregar (ejecuta a las 8:00 AM todos los días)
0 8 * * * cd /ruta/a/InforMessi && bash scripts/daily-flow.sh
```

---

## 📊 Estado Actual del Sistema

### ✅ Implementado

- [x] Recolección de datos (eventos, noticias)
- [x] Validación de noticias (fecha + contenido obsoleto)
- [x] Generación de mensajes con LLM
- [x] Secciones semanales automáticas
- [x] Scraper de Wikipedia para eventos históricos
- [x] Revisión humana en Telegram
- [x] Publicación en Telegram

### 🔄 Pendiente

- [ ] Automatización diaria (cron/n8n)
- [ ] Integración con n8n (workflows)
- [ ] Elementos visuales (imágenes/gifs)
- [ ] Publicación en otras plataformas (X, Instagram)
- [ ] Notion para revisión (futuro)

---

## 🎯 Próximos Pasos Recomendados

1. **Scrapear eventos de Wikipedia** (si no lo hiciste):
   ```bash
   python3 scripts/scrape-wikipedia-events.py --merge
   ```

2. **Probar flujo completo varias veces** para validar calidad

3. **Configurar automatización** (cron o n8n)

4. **Ajustar prompts** según resultados

5. **Agregar más eventos** a `data/events.json` manualmente

---

*El sistema está listo para uso diario. Solo falta automatizar la ejecución.*

