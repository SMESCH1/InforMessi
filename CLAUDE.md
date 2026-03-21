# InforMessi - CLAUDE.md

Pipeline editorial automatizado que genera y publica mensajes diarios sobre la Selección Argentina en el camino al Mundial 2026. Hay un humano en el loop: cada mensaje pasa por aprobación manual antes de publicarse en Telegram.

## Stack

- **Python 3.12** — todos los scripts
- **LLM**: Ollama local (dev) / Groq API `llama-3.1-8b-instant` (CI)
- **Telegram Bot API** — preview privado + publicación al canal
- **Flask + Render** — webhook para los botones de aprobación
- **GitHub Actions** — cron diario 10:15 AM ARG (13:15 UTC)
- **NewsAPI + Reddit (PRAW)** — fuente de noticias frescas

## Estructura del proyecto

```
data/
  events.json          # Eventos históricos, cumpleaños, partidos (match por MM-DD)
  memory-database.json # BD anti-repetición — solo actualizar al publicar
  players.json         # Perfiles de jugadores para secciones semanales
  templates.json       # Plantillas de formato
prompts/
  system-prompt.md     # Identidad editorial del LLM
  main-editorial.md    # Instrucciones de generación + ejemplos
  selection-prompt.md  # RAG paso 1: selección de evidencias
  constraints.md       # Restricciones de contenido
  examples.md          # Ejemplos de mensajes bien formados
reports/
  YYYY-MM-DD.json      # Un JSON por día: draft → updated → published
assets/
  media/YYYY-MM-DD/    # Imágenes/videos por fecha
  memes/               # Memes de fútbol argentino curados
scripts/               # Todos los scripts del pipeline (ver abajo)
docs/                  # Documentación técnica y editorial
.github/workflows/
  daily-informessi.yml # Workflow CI diario
```

## Pipeline diario

```
GitHub Actions (cron 13:15 UTC)
  ↓
generate-advance-reports.py   si no existe report del día
  ↓
update-today-report.py        agrega noticias frescas al report
  ↓
send-daily-report-review.py   envía preview a Telegram privado
  ↓
  [usuario aprueba / edita / rechaza via botones]
  ↓
publish-approved-report.py    publica al canal público
  ↓
auto-publish-fallback.py      fallback automático si no hay respuesta en 2h
  ↓
git commit & push (reports/ + data/)
```

## Scripts clave

| Script | Función |
|--------|---------|
| `collect-daily-data.py` | Recolecta eventos + noticias del día |
| `generate-message.py` | Llama al LLM con RAG en 2 pasos |
| `generate-advance-reports.py` | Genera N días de reports con antelación |
| `update-today-report.py` | Actualiza report con noticias frescas |
| `fetch-events-enhanced.py` | Busca eventos desde events.json + Wikipedia |
| `fetch-news.py` | Scraper de noticias deportivas |
| `generate-weekly-sections.py` | Construye prompt de sección semanal (jugador, dato mundialista, etc.) |
| `rag_memory_database.py` | BD persistente anti-repetición |
| `rag_style_learning.py` | Aprende estilo de reports aprobados |
| `send-daily-report-review.py` | Envía preview a Telegram |
| `publish-approved-report.py` | Publica al canal público + actualiza memoria |
| `auto-publish-fallback.py` | Publica automáticamente si no hay respuesta |
| `webhook-server.py` | Flask server para botones de Telegram |
| `update_memory_db.py` | Helper para actualizar memoria al publicar |

## Generación de mensajes: RAG en 2 pasos

1. **Selección** (`selection-prompt.md`): LLM elige los ítems más relevantes del día desde la lista de eventos/noticias. Temperatura baja (0.1), output JSON estricto.
2. **Generación** (`main-editorial.md`): LLM escribe el mensaje con los ítems seleccionados + contexto de memoria + sección semanal.

## Secciones semanales

| Día | Sección |
|-----|---------|
| Lunes / Viernes | Selección Argentina en Mundiales |
| Martes / Jueves | Jugador de la Scaloneta |
| Sábado | Dato Mundialista |
| Domingo | Dato del País Sede (EEUU / Canadá / México) |
| Miércoles | Formato estándar |

Los datos concretos para cada sección (perfiles de jugadores, datos mundialistas, datos de sedes) están en `data/players.json` y se inyectan directamente al prompt en `generate-weekly-sections.py`. **El LLM no debe inventar datos que no estén en el prompt.**

## Formato del mensaje generado

- **Longitud**: 90–130 palabras, texto plano, sin markdown
- **Estructura**: Saludo → Cuenta regresiva → Bloque principal → Sección del día → Dato del día → Cierre
- **Cierre ritual obligatorio**: "Coronados de gloria vivamos 🩵🤍🩵"
- **Emojis**: 3–5 por mensaje, estratégicamente distribuidos

## Sistema de memoria anti-repetición

`data/memory-database.json` rastrea:
- Jugadores mencionados y en qué fechas
- Secciones semanales usadas
- Noticias usadas (normalizado, últimos 30 días)
- Datos del día usados
- Temas generales (Mundial, Selección, etc.)

**Regla crítica**: la memoria se actualiza **solo al publicar** (en `publish-approved-report.py` y `auto-publish-fallback.py`). Nunca actualizar con drafts.

Para reconstruir la BD desde cero a partir de todos los reports publicados:
```bash
python3 scripts/rag_memory_database.py --update
```

## Eventos (`data/events.json`)

Los eventos matchean por **MM-DD** (no año), así funcionan como aniversarios anuales. Formato:

```json
{
  "date": "1986-06-22",
  "type": "world_cup",
  "priority": "high",
  "person": "Diego Maradona",
  "description": "La 'Mano de Dios' y el 'Gol del Siglo' contra Inglaterra."
}
```

Tipos: `birthday`, `match`, `title`, `world_cup`, `record`, `debut`, `failure`, `celebration`, `historical`
Prioridades: `high`, `medium`, `low`

Para birthdays, incluir `"age"` (edad que cumplen en 2026).

**Después de editar events.json, siempre validar:**
```bash
python3 -c "import json; data=json.load(open('data/events.json')); print(f'OK — {len(data[\"events\"])} eventos')"
```

## Variables de entorno

```
GROQ_API_KEY            # LLM en CI (Groq)
LLM_PROVIDER            # "ollama" (dev) | "groq" (CI)
LLM_MODEL               # Modelo a usar
LLM_BASE_URL            # URL de Ollama (dev)
TELEGRAM_BOT_TOKEN      # Token del bot
TELEGRAM_PREVIEW_CHAT_ID # Chat privado de revisión
TELEGRAM_PUBLIC_CHAT_ID  # Canal público
NEWSAPI_KEY             # Noticias (opcional)
REDDIT_CLIENT_ID        # Reddit PRAW (opcional)
REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT
```

En desarrollo: archivo `.env` en la raíz (no se commitea). En CI: GitHub Secrets.

## Tests

```bash
python3 -m pytest tests/ -v   # 43 tests unitarios
```

## Comandos frecuentes

```bash
# Generar reports anticipados (desde hoy, N días)
python3 scripts/generate-advance-reports.py --days 15

# Generar reports para un período específico
python3 scripts/generate-advance-reports.py --days 82 --start-date 2026-03-21

# Actualizar el report de hoy con noticias frescas
python3 scripts/update-today-report.py

# Ver qué sección corresponde a una fecha
python3 scripts/generate-weekly-sections.py --date 2026-04-07

# Reconstruir memoria desde todos los reports publicados
python3 scripts/rag_memory_database.py --update

# Ver estado de la memoria
python3 scripts/rag_memory_database.py --show

# Editar y validar un report manualmente
python3 scripts/edit-and-validate-report.py --date 2026-04-01

# Validar events.json
python3 -c "import json; data=json.load(open('data/events.json')); print(f'OK — {len(data[\"events\"])} eventos')"
```

## Reglas editoriales (no negociables)

1. **No inventar datos**: Si no está en events.json o en las noticias del día, no se menciona.
2. **No repetir noticias**: `collect-daily-data.py` filtra automáticamente noticias usadas en los últimos 7 días.
3. **Eventos primero**: Si hay evento del día, el mensaje gira alrededor de eso.
4. **Sección semanal con datos reales**: El LLM recibe perfiles y datos concretos — no debe improvisar.
5. **Memoria al publicar**: Actualizar `memory-database.json` solo cuando el report pasa a `status: published`.

## Contenido audiovisual

- **Imágenes/videos por fecha**: `assets/media/YYYY-MM-DD/`
- La imagen principal debe llamarse `01.jpg` o `principal.jpg`
- El sistema las detecta automáticamente via `detect-media.py`
- Para agregar metadata de recursos enlazados: `assets/media/YYYY-MM-DD/media-info.json`

## Convenciones de código

- Todo en Python 3.12, sin type hints en código no nuevo
- Scripts ejecutables directamente (`python3 scripts/nombre.py`)
- Logging con `logging.basicConfig` — no `print` para debugging
- JSON con `indent=2, ensure_ascii=False` al escribir archivos de datos
- Variables de entorno siempre via `os.environ.get()` con fallback claro

## Branch de trabajo

La branch activa es `refactor`. Main es la branch de producción.
