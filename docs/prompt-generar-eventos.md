# Prompt para generar eventos faltantes (21/3 → 11/6/2026)

Copiá esto en un LLM con acceso a internet y buena memoria histórica.
El output debe ser un array JSON que luego se agrega al archivo `data/events.json`.

---

## PROMPT A COPIAR

Necesito que generes datos históricos de fútbol argentino para completar un calendario editorial.
El sistema publica mensajes diarios sobre la Selección Argentina en el camino al Mundial 2026 (que empieza el 11/6/2026).

**Para cada fecha de la lista, necesito 1 o 2 eventos relevantes** siguiendo este formato JSON estricto:

```json
{
  "date": "YYYY-MM-DD",
  "type": "birthday|match|title|world_cup|record|failure|debut|historical",
  "priority": "high|medium|low",
  "person": "Nombre del jugador o 'N/A'",
  "description": "Descripción del evento en 1-2 oraciones, concreta y verificable",
  "age": 38
}
```

Notas sobre el formato:
- `date`: Usar el año histórico real del evento (ej: "1986-06-22", no "2026-06-22")
- `age`: Solo para birthdays, la edad que cumplen en 2026
- Prioridad `high`: el mensaje del día gira alrededor de este evento
- Prioridad `medium`: se menciona en el bloque principal
- Prioridad `low`: se menciona si hay espacio
- Las descripciones deben ser 100% verificables y precisas
- Evitar anécdotas no confirmadas

**Fechas que necesitan eventos (MM-DD, el año no importa para el matching):**

```
21/03 - marzo 21
22/03 - marzo 22
24/03 - marzo 24
26/03 - marzo 26
27/03 - marzo 27
28/03 - marzo 28
29/03 - marzo 29
31/03 - marzo 31
02/04 - abril 2
05/04 - abril 5
07/04 - abril 7
08/04 - abril 8
09/04 - abril 9
10/04 - abril 10
11/04 - abril 11
12/04 - abril 12
13/04 - abril 13
14/04 - abril 14
15/04 - abril 15
16/04 - abril 16
17/04 - abril 17
18/04 - abril 18
21/04 - abril 21
22/04 - abril 22
23/04 - abril 23
24/04 - abril 24
26/04 - abril 26
27/04 - abril 27
29/04 - abril 29
30/04 - abril 30
02/05 - mayo 2
03/05 - mayo 3
04/05 - mayo 4
05/05 - mayo 5
06/05 - mayo 6
07/05 - mayo 7
08/05 - mayo 8
11/05 - mayo 11
12/05 - mayo 12
15/05 - mayo 15
17/05 - mayo 17
21/05 - mayo 21
22/05 - mayo 22
23/05 - mayo 23
26/05 - mayo 26
28/05 - mayo 28
29/05 - mayo 29
31/05 - mayo 31
04/06 - junio 4
07/06 - junio 7
```

**Tipo de eventos deseados (en orden de preferencia):**

1. **Cumpleaños de jugadores** de la Selección Argentina (actuales o históricos):
   - Scaloneta actual: Messi (24/6), Di María (14/2), Dibu Martínez (2/9), Romero (8/10), De Paul (24/5), Mac Allister (24/12), Lautaro (22/8), Álvarez (31/1), Otamendi (12/2), Tagliafico (31/8), Enzo Fernández (17/1), Paredes (29/6), Montiel (1/1), Garnacho (1/7)
   - Jugadores históricos: Maradona (30/10), Batistuta (1/2), Kempes (15/7), Caniggia (9/1), Ortega, Saviola, Aimar, Ayala, Simeone, Burruchaga, Ruggeri, Passarella, Goycochea, Fillol, Ardiles, Gallardo, Tévez, Higuaín, Riquelme, Agüero (2/6), Mascherano (8/6), Crespo, Zanetti, Heinze

2. **Partidos históricos de la Selección** en esas fechas (exactas o aproximadas):
   - Goles importantes, victorias, derrotas recordadas, debuts legendarios
   - Clasificaciones a Mundiales (especialmente los sufridos: 2001, 2009, 2017)
   - Partidos de Copa América

3. **Efemérides mundialistas**:
   - Inauguraciones de Mundiales (1930, 1950, 1954, 1958, 1962, 1966...)
   - Goles o jugadas históricas de otros mundiales que sean interesantes para un canal argentino

**Ejemplos del formato esperado:**

```json
[
  {
    "date": "1961-03-21",
    "type": "birthday",
    "priority": "medium",
    "person": "Diego Simeone",
    "age": 65,
    "description": "Cumpleaños de Diego 'El Cholo' Simeone, campeón de América con Argentina en 1991 y 1993, hoy uno de los mejores técnicos del mundo."
  },
  {
    "date": "1997-03-29",
    "type": "match",
    "priority": "medium",
    "person": "Marcelo Gallardo",
    "description": "Argentina golea a Bolivia 3-1 en Buenos Aires por las Eliminatorias al Mundial Francia 98, con Gallardo y Batistuta en plenitud."
  },
  {
    "date": "1969-04-11",
    "type": "birthday",
    "priority": "high",
    "person": "Diego Simeone",
    "age": 57,
    "description": "Cumpleaños de Diego Pablo Simeone, 'El Cholo', ídolo de Independiente y la Selección bicampeona de América 91/93."
  }
]
```

**Output esperado:** Un array JSON con todos los eventos encontrados (puede haber más de uno por fecha). Solo incluir datos 100% verificados. Si no encontrás nada para una fecha específica, omitirla del output.

---

## Cómo cargar el resultado en el sistema

Una vez que tengas el JSON, buscá en `data/events.json` la línea que dice:

```json
        { "date": "2026-01-26", "type": "birthday", ...},
```

Y pegá los nuevos eventos a continuación, con coma separadora. Alternativa: ejecutar el script de validación:

```bash
python3 -c "import json; json.load(open('data/events.json')); print('JSON válido')"
```

---

## También necesito datos de partidos históricos como estos (para secciones Lunes/Viernes)

Para las secciones de "Selección Argentina en Mundiales" (Lunes y Viernes), si tenés acceso a datos precisos de:
- Todos los partidos de Argentina en todos los Mundiales con fecha exacta
- Goles, resultados, anécdotas verificables por partido
- Datos estadísticos: máximos goleadores, más partidos, más títulos, etc.

Los mismos entrarían al events.json con `"type": "world_cup"` y serían muy útiles.
