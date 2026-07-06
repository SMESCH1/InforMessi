# AI Engineering en InforMessi: patrones aplicados

Este documento explica la teoría detrás de cada patrón de AI Engineering aplicado
en este repo, cómo está implementado concretamente (con referencias a archivos
reales) y qué trade-offs se asumieron. No es un tutorial genérico: cada afirmación
es verificable en el código.

Contexto mínimo: InforMessi genera un mensaje editorial diario (Selección
Argentina + Mundial 2026) y lo publica en Telegram. La generación puede venir de
tres fuentes distintas, pero siempre pasa por el mismo gate de calidad antes de
llegar a una persona o a un canal público.

---

## 1. Arquitectura: separar generación de evaluación

### Teoría

Un LLM que genera contenido no debería ser también quien decide si ese contenido
está bien. Es el mismo principio que el code review: el autor de un cambio tiene
sesgo de confirmación sobre su propio trabajo, por eso lo revisa otra persona (u
otro proceso). En sistemas con LLMs el problema se agrava porque el modelo no
"sabe" cuándo alucinó: la salida incorrecta y la correcta le resultan igual de
fluidas. La solución arquitectónica es un contrato: el generador produce, un
evaluador independiente (programático, otro modelo, o un humano) decide.

### En este repo

Hay hasta **tres fuentes de generación** posibles para el mensaje de un día:

1. **Agente Claude** (`.claude/routines/daily-editorial.md`): un scheduled agent
   de Claude Code que corre a las 09:15 AR, hace web search, redacta el mensaje
   y commitea `reports/HOY.json` con `"source": "claude-agent"`.
2. **Fallback Groq** (`scripts/update-today-report.py`): si el agente no corrió,
   su report es de otro día ("stale") o no valida contra
   `scripts/report_schema.py`, el pipeline de las 10:15 AR regenera con
   `scripts/generate-message.py` (Groq `llama-3.3-70b-versatile`) y marca
   `"source": "groq-fallback"`.
3. **Base pre-generada** (`scripts/generate-advance-reports.py`): reports
   generados por adelantado con `"source": "pregenerated-base"`, que actúan como
   piso de resiliencia si todo lo demás falla ese día.

Las tres fuentes convergen en **el mismo gate**: el step "Evals (gate de
calidad)" de `.github/workflows/daily-informessi.yml` corre
`evals/run_evals.py --date HOY --gate --judge --on-fail regenerate` sin importar
de dónde salió el mensaje. El evaluador no sabe ni le importa quién generó.

Detalle importante: el agente Claude corre sus propias evals antes de commitear
(paso 9 de la routine), pero eso no lo exime del gate del pipeline. La routine
además codifica la regla "un commit malo es peor que no commitear": si tras 3
iteraciones las evals no pasan, el agente no commitea nada y el fallback Groq
toma el relevo. La auto-evaluación del agente es una optimización (falla rápido,
cerca de la fuente), no la autoridad final.

### Trade-offs

- Correr evals dos veces (agente + pipeline) cuesta tiempo y llamadas al judge.
  Se acepta porque el costo es marginal frente al costo de publicar un mensaje
  roto en un canal público.
- El contrato entre etapas es un archivo JSON en el repo (`reports/HOY.json`),
  no una cola de mensajes. Simple y auditable con `git log`, pero requiere
  cuidado con las carreras de push (el workflow hace `git pull --rebase` antes
  de pushear por eso).

---

## 2. Evals programáticas

### Teoría

Las *evals* (evaluaciones automáticas de salidas de un LLM) más baratas y
confiables son las programáticas: funciones puras que verifican propiedades
observables del texto. Son deterministas (mismo input, mismo resultado), cuestan
cero llamadas a API y corren en milisegundos, así que se pueden ejecutar en cada
generación, en CI y en tests. La clave de diseño es que no salen de la nada: se
**derivan de una spec**. Si existe un documento que define qué es un buen output,
cada regla verificable de ese documento se convierte en un check.

### En este repo

`evals/checks.py` implementa **10 checks** derivados de
`docs/editorial-guide.md` (la spec editorial del proyecto). Cada check retorna
`{"name", "passed", "severity", "detail"}`:

| Check | Severidad | Qué valida |
|---|---|---|
| `saludo` | error | Primera línea matchea `/^Buen(os)? día(s)?/` y contiene 🇦🇷 |
| `countdown_correcto` | error | La frase de cuenta regresiva es exactamente la que calcula `format_countdown()` para la fecha |
| `clima_presente` | error | Si hay `data.weather`, el bloque de clima existe y sus temperaturas coinciden dígito a dígito con los datos (sin datos de clima, el check se omite) |
| `sin_placeholders` | error | No hay `__`, `{...}`, `None`, `null`, ni frases con huecos ("enfrenta a  en") |
| `cierre_ritual` | error | Anteúltima línea "Buen día", última contiene "Coronados de gloria vivamos" |
| `años_grounded` | error | Todo año mencionado existe en los datos de entrada (ver sección 4) |
| `fecha_correcta` | error | `report["date"]` coincide con la fecha esperada; si `source=claude-agent`, `generated_at` convertido a hora argentina debe ser del mismo día |
| `longitud` | error/warning | 90-150 palabras pasa; 60-89 o 151-180 es warning; fuera de eso, error |
| `sin_markdown` | warning | Sin `**`, `##`, ` ``` ` (Telegram los mostraría literales) |
| `emojis` | warning | Entre 3 y 7 emojis (contando banderas de dos code points como uno) |

El **diseño de severidades** es una decisión de producto: `error` significa "esto
no puede llegar al canal" (estructura rota, dato inventado, placeholder);
`warning` significa "publicable pero mejorable" (un emoji de más no amerita
bloquear el envío de las 10:15). `longitud` es el caso interesante: tiene zona
gris explícita — un mensaje de 160 palabras es warning, uno de 200 es error.

`summarize()` colapsa los resultados en un **verdict**: `fail` si falló algún
error, `pass_with_warnings` si solo fallaron warnings, `pass` si no falló nada.
Ese string es el **contrato entre etapas**: `evals/run_evals.py` lo persiste en
`report["eval"]["verdict"]`, y los scripts aguas abajo
(`send-daily-report-review.py`, `auto-publish-fallback.py`) no re-evalúan nada —
solo leen el verdict y el flag `eval_warning` derivado de él.

### Cuándo no alcanzan

Un check programático puede verificar que el cierre ritual existe, pero no que
el tono sea "argentino, cercano, editorial, con humor sutil" — eso es calidad
subjetiva, no una propiedad decidible por regex. Un mensaje puede pasar los 10
checks y aun así sonar a chatbot genérico. Para esa capa está el judge
(sección 3). La regla práctica: **primero agotá lo programático** (barato,
determinista, sin falsos "sí" del modelo) **y recién después pagá el costo de
un LLM evaluador** para lo que quedó afuera.

---

## 3. LLM-as-judge

### Teoría

*LLM-as-judge* es usar un modelo como evaluador de las salidas de otro (o del
mismo) modelo. Funciona razonablemente bien para calidad subjetiva —tono,
coherencia, adherencia a una guía— pero tiene sesgos documentados que hay que
mitigar por diseño:

- **Self-preference bias**: un modelo tiende a puntuar mejor texto generado por
  sí mismo (o por modelos de su familia).
- **Position bias**: en comparaciones A/B, el orden de presentación afecta el
  veredicto (acá se evita evaluando un solo mensaje por vez con rúbrica
  absoluta, no comparativa).
- **Calibración de escala**: sin anclas, los modelos comprimen la escala hacia
  arriba (todo es 4 o 5). Los few-shot con ejemplos de score alto y bajo anclan
  los extremos.

Además, un judge no puede verificar "verdad universal" —no tiene acceso a la
realidad— pero sí puede verificar **groundedness**: ¿lo que afirma el mensaje
está respaldado por las fuentes que se le pasaron?

### En este repo

`evals/judge.py` + `prompts/judge-prompt.md`:

- **Modelos distintos para generar y juzgar**: el camino principal genera con
  Claude (agente) y juzga con `llama-3.3-70b-versatile` vía Groq. Esa separación
  neutraliza el self-preference bias en el flujo principal. (Limitación honesta:
  en el flujo fallback, Groq 70B genera y Groq 70B juzga — ahí el sesgo existe y
  se compensa con los checks programáticos, que no tienen sesgos.)
- **Temperatura 0 y JSON mode**: `judge_message()` llama con `temperature=0` y
  `response_format={"type": "json_object"}` (vía `scripts/llm_client.py`). El
  judge debe ser lo más determinista y parseable posible; la creatividad acá es
  un defecto.
- **Rúbrica con dimensiones acotadas**: 4 dimensiones (`tono`, `estructura`,
  `fidelidad_guia`, `factualidad_aparente`), cada una 1-5 con criterios
  explícitos en el prompt. Dimensiones pocas y ortogonales rinden más que un
  "score general" opaco.
- **Few-shot de calibración**: `judge-prompt.md` incluye un ejemplo de mensaje
  bueno (todo 5) y uno roto (1-2), con la salida JSON esperada para cada uno.
- **Groundedness, no verdad**: el user prompt arma un bloque "Datos fuente
  (evaluar el mensaje SOLO contra esto)" con `events`, `news` y `weather`, y el
  system prompt es explícito: si un dato no está en las fuentes, es alucinación
  *aunque al modelo le suene cierto*. La dimensión se llama
  `factualidad_aparente` a propósito: mide consistencia con las fuentes, no
  verdad absoluta.
- **Validación dura de la salida**: `_parse_and_validate()` exige las 4
  dimensiones numéricas en rango 1-5; rechaza booleanos, campos faltantes y
  valores fuera de rango. Si el modelo envolvió el JSON en texto, hay un único
  reintento de parseo extrayendo el primer bloque `{...}`.
- **Best-effort por diseño**: cualquier falla (API caída, JSON inválido)
  devuelve `None` y el pipeline sigue solo con los checks programáticos. El
  judge es una capa adicional de señal, no un single point of failure.

El **umbral** está en `evals/run_evals.py::compute_verdict()`: promedio de las 4
dimensiones `< 3.0` fuerza verdict `fail`. Es una decisión de producto, no una
constante técnica: 3.0 es el punto medio de la escala ("ni bueno ni malo"), y el
costo de un falso positivo (bloquear un mensaje decente → lo revisa un humano)
es mucho menor que el de un falso negativo (publicar un mensaje malo en el
canal). Con datos de `data/eval-history.json` (sección 7) el umbral se puede
recalibrar empíricamente.

### Limitaciones asumidas

- Un judge de 70B se equivoca; por eso su `fail` no publica automáticamente una
  corrección, sino que degrada a revisión humana (sección 6).
- Una escala 1-5 con temperature 0 es una señal gruesa: sirve para un gate
  binario con umbral, no para análisis fino de calidad. Si hiciera falta más
  resolución, el camino sería una rúbrica más granular o comparaciones
  pareadas — con el costo de calibración que eso implica.

---

## 4. Grounding y anti-alucinación

### Teoría

*Grounding* es garantizar que lo que el modelo afirma esté anclado en datos
provistos, no en su memoria paramétrica. No todas las defensas valen lo mismo;
conviene pensarlas como una jerarquía de confiabilidad decreciente:

1. **Inyección determinística**: el dato ni siquiera pasa por el modelo — lo
   inserta código. Probabilidad de alucinación: cero.
2. **Validación post-generación contra whitelist**: el modelo genera, código
   verifica cada entidad contra los datos de entrada y elimina lo que no matchea.
3. **Verificación multi-fuente en la recolección**: el dato entra al sistema
   solo si se confirmó en fuentes independientes.
4. **Instrucciones de prompt**: "no inventes X". La capa más débil — el modelo
   puede ignorarla — pero reduce la frecuencia de violaciones que las capas
   anteriores tienen que atrapar.

El orden importa: lo determinístico no puede alucinar, así que todo dato que
pueda inyectarse por código debería inyectarse por código. El prompt es la
última línea de defensa, no la primera.

### En este repo

**(a) Clima inyectado determinísticamente.** El LLM tiene *prohibido* escribir
temperaturas (`prompts/system-prompt.md`: "NO escribas ningún bloque de clima
ni menciones temperaturas"). El bloque se construye con datos de Open-Meteo
(`scripts/fetch-weather.py::format_weather_block`) y lo inserta
`postprocess_message()` en `scripts/generate-message.py` después de la línea de
countdown (`_inject_weather_block`). Como defensa extra,
`_strip_llm_weather_mentions()` elimina cualquier línea donde el LLM haya
hablado del clima igual — con patrones acotados a contexto meteorológico real,
para no borrar frases como "el clima tenso del vestuario" (falso positivo
confirmado empíricamente y documentado en el código). Y el check
`clima_presente` de `evals/checks.py` cierra el círculo: compara las
temperaturas del mensaje final dígito a dígito contra `data.weather`.

**(b) Whitelist de entidades post-generación.**
`_extract_allowed_entities()` en `scripts/generate-message.py` extrae de los
eventos y noticias de entrada los años, personas y resultados (scores tipo
"4-0") permitidos. `postprocess_message()` busca años en el mensaje generado y
**elimina la línea completa** que contenga un año no presente en los datos (más
un set fijo de años de contexto: 2026, 2025, 1978, 1986, 2022 — las fechas
estructurales del proyecto). Si tras la limpieza el mensaje queda vacío, cae a
un mensaje mínimo seguro (`_build_safe_message`: saludo + countdown + clima +
cierre). El mismo criterio se re-verifica en el gate con el check
`años_grounded`, que usa la misma función — generador y evaluador comparten la
definición de "permitido", no hay dos listas que puedan divergir.

**(c) Web search con verificación multi-fuente.** La routine del agente
(`.claude/routines/daily-editorial.md`, paso 4) exige que cualquier dato
(resultado, horario, convocatoria) esté confirmado en **al menos 2 fuentes
independientes**; ante la duda se omite. Las URLs verificadas quedan en
`data.sources`, que `scripts/report_schema.py` valida como lista no vacía de
URLs http(s) para todo report con `source=claude-agent`.

**(d) Instrucciones de prompt.** `prompts/system-prompt.md` prohíbe inventar
datos, cumpleaños, estadísticas y frases genéricas sin respaldo, y distingue
explícitamente efemérides (pasado) de eventos del día (presente). Además hay
una regla estructural: si no hay eventos ni noticias, el mensaje debe ser solo
saludo + countdown + cierre — y `postprocess_message()` la refuerza
programáticamente descartando contenido extra en ese caso (Regla 1).

### Trade-offs

- La eliminación de líneas con años alucinados es quirúrgica pero destructiva:
  puede llevarse una frase válida que compartía línea. Se prefiere perder una
  frase a publicar un año inventado.
- La whitelist fija de años de contexto es una concesión pragmática: sin ella,
  mencionar "campeones en Qatar 2022" fallaría siempre que 2022 no esté en los
  datos del día.

---

## 5. RAG anti-repetición

### Teoría

El RAG clásico (*Retrieval-Augmented Generation*) recupera contexto relevante
para que el modelo lo **use**. Acá el patrón está invertido: se recupera lo ya
publicado para inyectarlo como **contexto negativo** — "esto ya se dijo, no lo
repitas". Un informativo diario que menciona al mismo jugador tres días seguidos
o recicla el mismo dato curioso pierde credibilidad; el problema no es falta de
información sino exceso de repetición, y la memoria del sistema (no la del
modelo, que es stateless entre corridas) es lo que lo resuelve.

### En este repo

Tres componentes, todos consumidos por `build_prompt()` en
`scripts/generate-message.py`:

1. **`scripts/rag_memory_database.py`** — memoria persistente en
   `data/memory-database.json`: jugadores mencionados, temas, eventos, noticias,
   datos y frases usadas, cada uno con las fechas en que aparecieron.
   `build_memory_context_from_db()` genera el bloque de contexto negativo para
   el prompt. Detalle de diseño: la memoria **se actualiza solo al publicar**
   (no al generar drafts), para que un borrador descartado no "queme" contenido
   que nunca llegó al canal.
2. **`scripts/rag_memory_system.py`** — fallback basado en archivos: lee los
   reports de los últimos 30 días directamente de `reports/` y extrae qué se
   usó. Es el plan B si la base de datos no está disponible (el `try/except` de
   `build_prompt` cae a este sistema).
3. **`scripts/rag_style_learning.py`** — la variante positiva: extrae snippets
   de reports con status `updated` o `published` (es decir, que pasaron por
   edición humana o llegaron al canal) y los inyecta como few-shot examples de
   estilo. Los mensajes que el humano aprobó definen el tono a imitar.

El agente Claude participa del mismo sistema por contrato: el paso 6 de su
routine le exige consultar `data/memory-database.json` antes de elegir ángulo,
y el paso 10 le prohíbe escribirla (la memoria se actualiza al publicar, en un
solo lugar).

### Trade-offs

- La memoria es un archivo JSON, no un vector store: la búsqueda es por match
  de strings normalizados, no semántica. "Messi" y "Leo" no colapsan solos. Para
  el volumen del proyecto (un mensaje diario) es suficiente y debuggeable a ojo.
- Contexto negativo en el prompt es una instrucción más que el modelo puede
  ignorar; no hay check programático de repetición en el gate (mejora posible:
  un check de n-gramas contra los últimos N mensajes).

---

## 6. Human-in-the-loop y circuit breakers

### Teoría

Automatizar la publicación de contenido generado por LLM no es una decisión
binaria sino un **espectro de autonomía**: desde "un humano aprueba todo"
hasta "se publica solo". El diseño maduro es adaptativo: el nivel de autonomía
depende de la confianza que el propio sistema tiene en el output. Un *circuit
breaker* es el mecanismo que degrada la autonomía automáticamente cuando algo
huele mal: no intenta arreglar el problema, corta el circuito y exige
intervención.

### En este repo

El pipeline tiene tres niveles de autonomía, según el estado del report:

1. **Publicación directa** — si `pre_approved=True` y no hay `eval_warning`,
   `scripts/send-daily-report-review.py` publica directo al canal sin preview.
   Es el camino del fallback Groq que pasó las evals
   (`update-today-report.py` setea `pre_approved=True` al regenerar).
2. **Preview + timeout** — el camino normal del agente Claude (la routine
   commitea con `pre_approved: false` y el pipeline no lo toca): preview al
   chat privado de Telegram con botones de aprobación, y si el humano no
   responde, `scripts/auto-publish-fallback.py` publica tras 2 horas
   (`--check-all --hours 2` en el workflow). El timeout es el compromiso
   disponibilidad/control: el informativo debe salir todos los días aunque el
   editor esté durmiendo, pero le da una ventana real para vetar.
3. **Supervisión obligatoria** — el circuit breaker. Si el verdict final es
   `fail`, `evals/run_evals.py` marca `eval_warning: true` y fuerza
   `pre_approved: false`. A partir de ahí:
   - `send-daily-report-review.py` antepone un header de advertencia al preview
     (`build_eval_warning_header()` lista los checks de error que fallaron) y
     nunca publica directo (`if report.get("pre_approved") and not
     report.get("eval_warning")`).
   - `auto-publish-fallback.py` retorna `False` incondicionalmente ante
     `eval_warning` — un report marcado no se auto-publica *nunca*, sin importar
     cuánto tiempo pase.
   - Solo la edición + aprobación manual destraban la publicación de ese día.

El flag se limpia solo con evidencia: si una corrida posterior de evals da
`pass`/`pass_with_warnings`, `run_evals.py` remueve `eval_warning`. El sistema
puede volver a autonomía alta, pero únicamente pasando de nuevo por el gate.

### Trade-offs

- El timeout de 2 horas implica que un mensaje mediocre-pero-aprobable puede
  publicarse sin ojos humanos. Es deliberado: los mensajes que las evals
  consideran peligrosos ya quedaron atrapados por el breaker; lo que llega al
  timeout pasó 10 checks + judge.
- `eval_warning` es un booleano, no un score: no distingue "falló por una
  palabra de más" de "inventó un resultado". El detalle queda en
  `report["eval"]["checks"]` y en el header del preview, donde el humano lo ve.

---

## 7. Métricas y mejora continua

### Teoría

Sin métricas longitudinales, iterar prompts es adivinar: cambiás una
instrucción, el mensaje de hoy sale bien, y no sabés si fue el cambio o suerte.
*Eval-driven development* es tratar los prompts como código con tests: cada
corrida de evals appendea a un dataset histórico, y un cambio de prompt se
valida comparando la distribución de scores antes/después, no con una anécdota.

### En este repo

Cada corrida de `evals/run_evals.py` appendea una entrada a
`data/eval-history.json` (`_append_history()`):

```json
{
  "date": "...", "run_at": "...",
  "source": "claude-agent | groq-fallback | pregenerated-base",
  "model": "llama-3.3-70b-versatile",
  "checks_passed": 10, "checks_failed": 0, "warnings_failed": 0,
  "judge_scores": {"tono": 4, "estructura": 5, "fidelidad_guia": 5,
                   "factualidad_aparente": 4, "promedio": 4.5},
  "verdict": "pass"
}
```

La clave del diseño es el campo **`source`**: como las tres fuentes de
generación pasan por el mismo gate, el historial permite comparar manzanas con
manzanas — ¿los mensajes del agente Claude puntúan mejor en `tono` que los del
fallback Groq? ¿la base pre-generada falla más `años_grounded`? Esa comparación
es imposible si cada generador tiene su propia vara.

Usos concretos que habilita el dataset:

- **Iterar prompts con evidencia**: cambiar `prompts/system-prompt.md`, correr
  `python evals/run_evals.py --range A:B --judge` sobre un rango de reports
  regenerados, y comparar verdicts y promedios del judge contra el período
  anterior. El modo `--range` existe exactamente para este backfill/baseline.
- **Recalibrar el umbral del judge** (hoy promedio < 3.0) mirando la
  distribución real de scores en vez de intuición.
- **Detectar regresiones de proveedor**: si Groq cambia el modelo detrás del
  alias, la serie histórica lo muestra antes que un usuario.

Estado actual honesto: el archivo se genera en runtime y el baseline inicial
(regenerar los reports base de julio 2026 y evaluarlos con judge) está
scripteado en `scripts/regenerate-base-reports.sh`, pendiente de correr con
`GROQ_API_KEY` disponible. La infraestructura de medición está completa; el
dataset se acumula corrida a corrida.

Robustez del dataset: si `eval-history.json` aparece corrupto, `run_evals.py`
lo respalda como `.bak` antes de arrancar una lista nueva
(`_backup_corrupt_history()`) — no se pierde historia silenciosamente.

---

## 8. Lecciones aprendidas

Cosas que salieron mal (o casi) en este repo, y qué patrón general ilustran.

### Timezone en CI: "hoy juegan" para partidos de ayer

El bug real (fix en commit `4328327`, base en `dd671b7`): los runners de GitHub
Actions corren en UTC, y el pipeline usaba `datetime.now()` naive, que en ese
entorno devuelve fecha y hora UTC, no argentinas. Durante la ventana diaria en
que la fecha UTC ya cambió pero la argentina todavía no (Argentina es UTC-3),
el pipeline calculaba "hoy" con el día equivocado — con el resultado de
presentar partidos de ayer como si fueran de hoy. El síntoma es traicionero
porque el código es correcto la mayor parte del día y solo falla si el job
corre en esa ventana.

El fix fue estructural, no puntual: `scripts/time_utils.py` centraliza
`now_ar()` / `today_ar()` / `parse_ts()` con `ZoneInfo("America/Argentina/
Buenos_Aires")`, y se reemplazó todo `datetime.now()` del pipeline (17 scripts).
`parse_ts()` además asume TZ argentina para timestamps naive viejos, para no
romper compatibilidad con reports históricos. La lección quedó codificada en
tres lugares más: la routine del agente ordena calcular HOY en TZ argentina
"NUNCA en UTC" (paso 1), `report_schema.py` rechaza `generated_at` sin offset
explícito para reports del agente, y el check `fecha_correcta` verifica que
`generated_at` convertido a hora argentina coincida con `report["date"]`. Un
bug de entorno se convirtió en cuatro validaciones permanentes.

### Límites de modelos chicos: 8B → 70B

El pipeline arrancó con `llama-3.1-8b-instant`. Cuando los prompts se
reescribieron para exigir estructura editorial completa —7 bloques ordenados,
narrativa desarrollada, cierre doble, prohibiciones de grounding
(`6acc28b`)— el 8B no seguía instrucciones con esa densidad de manera confiable.
El bump a `llama-3.3-70b-versatile` (commits `6d30150` y `698f73d`) acompañó esa
reescritura. Lección: la capacidad de *instruction following* escala con el
tamaño del modelo, y un prompt sofisticado sobre un modelo chico produce peor
resultado que un prompt simple — el prompt y el modelo se eligen juntos, no por
separado.

### max_tokens como causa de truncamiento

Junto con el bump de modelo, `max_tokens` de generación pasó de 300 a 500
(`6d30150`: "más espacio para narrativa editorial"). Con 300 tokens, un mensaje
de estructura completa corría riesgo de cortarse a mitad de camino — y un
mensaje truncado pierde justamente el final, es decir el cierre ritual, que es
un check de severidad `error`. Lección doble: (1) `max_tokens` es un límite de
corte duro, no una sugerencia de longitud — la longitud se controla en el
prompt y se valida en evals (`check_longitud`); (2) cuando un output llega
sistemáticamente incompleto, revisar los parámetros de sampling antes de culpar
al prompt.

### Determinismo vs. generación: el bloque de clima

La opción obvia sería pasarle las temperaturas al LLM en el prompt y pedirle
que escriba el bloque de clima. Problema: un modelo puede redondear, mezclar
mínima con máxima o "embellecer" un número, y un dato numérico incorrecto en un
informativo es inaceptable. Acá la responsabilidad está invertida: el LLM tiene
prohibido mencionar el clima (`prompts/system-prompt.md`), el bloque lo
construye código determinístico (`fetch-weather.py::format_weather_block`) y lo
inyecta el post-proceso (`_inject_weather_block`). Que la prohibición sola no
alcanza está documentado en el propio código: el comentario de
`_strip_llm_weather_mentions` en `scripts/generate-message.py` registra que el
LLM "a veces escribe" líneas de clima pese a la instrucción explícita — por eso
existe el filtro. Lección: **si un dato tiene una única forma correcta, no le
pidas a un modelo generativo que lo escriba** — la generación es para la prosa,
no para los números.

### Pre-generación como estrategia de resiliencia

El sistema depende de servicios externos que fallan: web search, Groq, NewsAPI,
Open-Meteo. La defensa de última línea es que `reports/` ya contenga un report
base para cada fecha próxima, generado por adelantado con
`scripts/generate-advance-reports.py` y marcado `"source":
"pregenerated-base"`. Si el agente no corre y Groq está caído, hay contenido
publicable — menos fresco, pero estructuralmente válido y evaluado por el mismo
gate. Es la versión editorial de *graceful degradation*: cada capa de
generación puede fallar, y la disponibilidad del mensaje diario no depende de
ninguna en particular. El marcado explícito del `source` hace además que esta
degradación sea medible (sección 7): se puede saber cuántos días publicó cada
fuente y con qué calidad.

---

## Índice de archivos citados

| Archivo | Rol |
|---|---|
| `.claude/routines/daily-editorial.md` | Routine del agente generador (09:15 AR) |
| `.github/workflows/daily-informessi.yml` | Pipeline evaluador/publicador (10:15 AR) |
| `.github/workflows/daily-news-scraper.yml` | Scraper de noticias (04:00 AR) |
| `evals/checks.py` | 10 checks programáticos |
| `evals/judge.py` | LLM-as-judge (Groq 70B, temp 0, JSON mode) |
| `evals/run_evals.py` | Orquestador: verdict, gate, historial, regeneración |
| `prompts/judge-prompt.md` | Rúbrica + few-shot del judge |
| `prompts/system-prompt.md` | Reglas de generación y grounding |
| `scripts/generate-message.py` | Generación + post-proceso anti-alucinación |
| `scripts/update-today-report.py` | Detección del report del agente / fallback Groq |
| `scripts/report_schema.py` | Validación aditiva del contrato de reports |
| `scripts/send-daily-report-review.py` | Preview Telegram + header de eval_warning |
| `scripts/auto-publish-fallback.py` | Auto-publish 2h, bloqueado por eval_warning |
| `scripts/fetch-weather.py` | Clima determinístico (Open-Meteo) |
| `scripts/rag_memory_database.py` | Memoria persistente anti-repetición |
| `scripts/rag_memory_system.py` | Memoria fallback (reports de 30 días) |
| `scripts/rag_style_learning.py` | Few-shot de estilo desde reports aprobados |
| `scripts/time_utils.py` | Timezone Argentina centralizado (lección del bug de CI) |
| `scripts/generate-advance-reports.py` | Base pre-generada (`pregenerated-base`) |
| `scripts/regenerate-base-reports.sh` | Regeneración de base + baseline de evals |
| `data/eval-history.json` | Dataset longitudinal de evals (generado en runtime) |
| `docs/editorial-guide.md` | Spec editorial de la que derivan los checks |
| `docs/agente-diario.md` | Contrato agente ↔ pipeline |
