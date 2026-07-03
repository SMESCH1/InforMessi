# Routine: Editorial diaria de InforMessi (agente Claude)

Corre en cloud, cron `15 12 * * *` UTC = 09:15 hora Argentina, ~1 hora antes
del workflow de GitHub Actions (10:15 AR). Tenés acceso al repo InforMessi y
a WebSearch. Objetivo: generar la editorial del día con datos frescos
verificados y dejarla commiteada en `reports/HOY.json` para que el pipeline
Groq la detecte, la valide y salte su propia regeneración.

Si en cualquier paso no podés cumplir el requisito (búsqueda web caída, sin
datos confiables, validación de evals no pasa tras los reintentos), NO
commitees nada — el pipeline Groq de las 10:15 genera el fallback. Un
commit malo es peor que no commitear.

## Pasos

### 1. Calcular la fecha de hoy

Calculá HOY en `America/Argentina/Buenos_Aires` (UTC-3), NUNCA en UTC — un
cálculo en UTC puede dar el día equivocado según la hora de corrida. Usá esa
fecha (formato `YYYY-MM-DD`) para todo lo que sigue: nombre del archivo
report, campo `date`, búsquedas, etc.

### 2. Leer la guía editorial

Leé, en este orden:
- `docs/editorial-guide.md` — identidad, tono, estructura de 7 bloques, longitud, reglas de contenido.
- `prompts/system-prompt.md` — reglas críticas de redacción (grounding, formato de fechas, prohibiciones).
- `prompts/main-editorial.md` — reglas de uso de datos, secciones especiales por día de la semana, ejemplos de mensajes bien formados.

No te apartes de estas reglas: son la fuente de verdad del tono y formato
del proyecto, evaluadas después por `evals/checks.py` y el judge LLM.

### 3. Leer el report base de hoy (si existe)

Si `reports/HOY.json` (con HOY = la fecha calculada en el paso 1) ya existe
—generado por un run anterior del pipeline Groq o de un día previo de este
mismo agente—, usalo como base. Actualizalo con los datos frescos que
consigas en los pasos siguientes, pero:
- Conservá eventos históricos válidos que ya estén en `data.events` (no los
  borres solo porque no aparecen en tu búsqueda de hoy).
- No pises ciegamente: mergeá, no reemplaces el archivo entero sin revisar
  qué había.

Si no existe, arrancás desde cero.

### 4. Búsqueda web con verificación en al menos 2 fuentes

Buscá, en este orden de prioridad:

a) **Partidos del Mundial 2026 de HOY**, con prioridad para los que juega
   Argentina: rival, hora argentina (UTC-3), estadio, ciudad.
b) **Resultados de AYER** relevantes (partidos importantes, resultado de
   Argentina si jugó).
c) **1 a 3 noticias frescas de la Selección Argentina** (convocatorias,
   lesiones, declaraciones, entrenamientos — fútbol únicamente).

Reglas estrictas:
- **Prohibido** política, farándula, o cualquier tema no futbolístico.
- Cualquier dato (resultado, horario, convocatoria, cifra) que no puedas
  confirmar en **al menos 2 fuentes independientes** NO va al mensaje. Ante
  la duda, se omite — no se arriesga con un dato a medias.
- Guardá las URLs verificadas: las vas a necesitar en `data.sources` (paso 8).

### 5. Clima

Ejecutá:

```
python scripts/fetch-weather.py --date HOY --json
```

(con HOY la fecha del paso 1). Usá EXACTAMENTE los números que devuelve ese
comando — nunca inventes ni redondees distinto una temperatura. Si el
comando falla o devuelve `null`, omitís el bloque de clima entero en el
mensaje (no inventes un bloque de clima ni pongas placeholders).

### 6. Consultar la memoria para no repetir contenido

Revisá `data/memory-database.json`: jugadores, temas y noticias usados
recientemente. Si algo que ibas a usar ya se mencionó hace poco, priorizá
otro ángulo o dato para no repetir editorial.

### 7. Escribir el mensaje

Redactá el mensaje completo siguiendo la guía del paso 2, incluyendo el
bloque de clima con el formato exacto de
`scripts/fetch-weather.py::format_weather_block` (mismo texto, mismos
labels "AMBA" / "La Plata", mismo link del SMN). Usá SOLO los datos
verificados en los pasos 4 y 5. No inventes estadísticas, cumpleaños ni
curiosidades que no estén respaldadas por lo que recolectaste.

### 8. Guardar `reports/HOY.json`

Guardalo PRIMERO (antes de correr evals), manteniendo el formato general
que ya usa el repo (mismas claves de siempre: `date`, `data`, `message`,
`status`, `pre_approved`, etc. — no borres claves existentes del report
base del paso 3) y seteando/agregando:

- `"source": "claude-agent"`
- `"generated_at"`: timestamp ISO con offset `-03:00` explícito (ej.
  `"2026-07-03T09:20:00-03:00"`) — NUNCA naive, NUNCA solo UTC sin offset.
- `"status": "agent-draft"`
- `"pre_approved": false`
- `data.events`: los partidos/efemérides que efectivamente usaste.
- `data.news`: las noticias usadas, cada una con `title`, `description`,
  `source` (y `url` si la tenés).
- `data.weather`: el objeto devuelto por el paso 5, o `null` explícito si
  no se pudo obtener (la clave debe existir siempre).
- `data.sources`: lista de URLs http(s) que verificaste en el paso 4 (no
  vacía).
- `"message"`: el mensaje completo del paso 7.

### 9. Correr evals y corregir si hace falta

Ejecutá:

```
python evals/run_evals.py --date HOY --gate --judge
```

Si algún check de severidad `error` falla, corregí el mensaje (respetando
siempre los datos verificados — no "arregles" un check inventando algo) y
volvé a guardar `reports/HOY.json`, después repetí este paso. Máximo 3
iteraciones en total. Si tras 3 iteraciones sigue fallando, dejá guardada
la última versión (con su `eval` block) y NO commitees — andá directo al
paso 11.

### 10. Commit y push

Si las evals pasan (o quedan en `pass_with_warnings`), commiteá **solo**
`reports/HOY.json` — ningún otro archivo — con mensaje:

```
Editorial HOY (claude-agent)
```

(reemplazando HOY por la fecha real, ej. `Editorial 2026-07-03
(claude-agent)`) y hacé push a `main`. No toques `data/memory-database.json`
ni ningún otro archivo del repo: la memoria se actualiza sola al momento de
publicar, no en este paso.

### 11. Si no hay info confiable

Si la búsqueda web falla por completo, o ningún dato relevante del día pasa
la verificación de 2 fuentes, o las evals nunca pasan tras 3 intentos: NO
commitees nada. Terminá la sesión sin tocar el repo. El pipeline de GitHub
Actions de las 10:15 AR va a generar el fallback con Groq usando
`data/events.json` como fixture.
