# Agente diario (Claude) — contrato con el pipeline

Documenta cómo interactúan el scheduled agent de Claude Code (routine
`.claude/routines/daily-editorial.md`) y el pipeline de GitHub Actions
(`.github/workflows/daily-informessi.yml`) para generar la editorial diaria.

## Horarios (hora Argentina, UTC-3)

| Hora  | Qué corre | Dónde |
|-------|-----------|-------|
| 04:00 | Scraper de noticias/eventos (`daily-news-scraper.yml`) | GitHub Actions |
| 09:15 | Agente Claude: genera la editorial con web search | Routine cloud (`daily-editorial.md`) |
| 10:15 | Pipeline diario: detecta el report, corre evals, publica | GitHub Actions (`daily-informessi.yml`) |

El agente corre ~1 hora antes que el pipeline para darle margen a manejar
fallas de búsqueda o de evals (hasta 3 reintentos) sin comprometer el envío
de las 10:15.

## Formato del report del agente

Cuando el agente commitea `reports/YYYY-MM-DD.json`, además de los campos
que ya usa cualquier report (`date`, `data.events`, `data.news`, `message`,
`status`, `pre_approved`), agrega:

- `"source": "claude-agent"` — marca de origen, lo que dispara la detección
  en `scripts/update-today-report.py` y las validaciones extra de
  `scripts/report_schema.py`.
- `"generated_at"` — ISO con offset de timezone explícito (`-03:00` o `Z`).
  Nunca naive: se usa para decidir si el report es "de hoy" en hora
  argentina.
- `"data.weather"` — dict con `amba`/`la_plata` (o `null` explícito si
  `fetch-weather.py` falló). La clave debe existir siempre.
- `"data.sources"` — lista no vacía de URLs http(s) verificadas en la
  búsqueda web.

El schema completo y su validación programática están en
`scripts/report_schema.py::validate_report`. La validación es **aditiva**:
reports viejos (sin `source`) nunca fallan por los campos nuevos.

## Cómo lo detecta el pipeline

En `scripts/update-today-report.py::update_report_for_date`, apenas se
carga el report existente:

1. Si `report["source"] != "claude-agent"` → sigue el flujo normal
   (regeneración con Groq).
2. Si es `"claude-agent"`:
   - Se compara `generated_at` (convertido a fecha AR) contra la fecha que
     se está procesando. Si no coincide (report de otro día, "stale"), se
     regenera con Groq.
   - Si coincide pero falta `message`, también se regenera con Groq.
   - Si coincide y `validate_report()` no encuentra errores, el pipeline
     **acepta el report tal cual**: solo actualiza `updated_at` (para que
     el flujo de auto-publish, que mira ese campo, funcione) y NO toca
     `pre_approved` — la aprobación manual/preview sigue el camino de
     siempre. No se llama a Groq en absoluto.
   - Si coincide pero `validate_report()` encuentra errores, se loguea el
     motivo y se regenera con Groq.

Cuando el pipeline efectivamente regenera con Groq (report stale, inválido,
o inexistente el aporte del agente), el report resultante queda marcado con
`"source": "groq-fallback"`.

## Qué pasa si el agente no corre (o falla)

`reports/HOY.json` nunca se actualiza con `source: claude-agent`, o queda
con `generated_at` de un día anterior. El pipeline de las 10:15 lo trata
como cualquier report sin agente: lo regenera con Groq 70B usando
`data/events.json` como fixture y las noticias recolectadas por el scraper
de las 04:00. El resto del flujo (evals, Telegram, auto-publish) es
idéntico. El sistema nunca depende de que el agente haya corrido.

## Qué pasa si las evals fallan

Tanto si el mensaje viene del agente como de Groq, el step "Evals (gate de
calidad)" corre `evals/run_evals.py --date HOY --gate --judge --on-fail
regenerate`:

- Si el veredicto final (tras el intento de regeneración) es `fail`, el
  report queda con `eval_warning: true` y `pre_approved: false`.
- `send-daily-report-review.py` respeta `eval_warning`: el preview a
  Telegram incluye un header de advertencia en vez de mandarlo como si
  nada.
- `auto-publish-fallback.py` respeta `eval_warning`: un report marcado
  nunca se auto-publica, sin importar cuánto tiempo pase.
- Se requiere intervención manual (edición + aprobación) para publicar ese
  día.

## Prioridad del agente sobre `data/events.json`

`data/events.json` es el fixture estático que usa el pipeline Groq como
fuente de eventos/efemérides cuando no hay nada más fresco. El agente, en
cambio, corre web search en el momento y puede confirmar partidos,
resultados y noticias del día que el fixture no tiene o tiene desactualizados.

Regla general: **la frescura gana**. Si el agente generó un report válido y
del día correcto, el pipeline lo usa tal cual y no consulta
`data/events.json` en absoluto (ese path solo se ejecuta en el flujo Groq).
Esto significa que un partido de último momento, un cambio de horario, o
una noticia de último momento reportada por el agente siempre tiene
prioridad sobre el fixture estático.
