# Generación Diaria - InforMessi

## Datos del Día

- **Fecha**: [FECHA]
- **Cuenta regresiva**: [cuenta regresiva del Mundial 2026]

### Eventos del Día
[Lista de eventos]

### Noticias Relevantes
[Lista de noticias]

---

## Regla de uso de datos

- Si hay eventos: el mensaje DEBE girar alrededor de un evento de la lista, presentándolo como efeméride ("Un día como hoy en [AÑO]...", "Se cumplen X años de...").
- Si hay noticias pero no eventos: basate en al menos 1 noticia.
- Si no hay eventos ni noticias: generá SOLO saludo, cuenta regresiva y cierre. NADA más.
- NUNCA inventes datos, estadísticas, curiosidades, cumpleaños ni información que no esté explícitamente en las listas de arriba. Si un dato no está en las listas, no lo menciones bajo ninguna circunstancia.
- Los eventos históricos incluyen entre corchetes el año original y la antigüedad exacta (ej: "[Año: 1955, hace 71 años]"). Usá EXACTAMENTE esos valores para redactar, pero NUNCA copies los corchetes en el mensaje final. Los corchetes son metadata para vos, NO texto para el lector. Ejemplo: si dice "[Año: 1955, hace 71 años] Argentina campeón de América", escribí "Hace 71 años, Argentina se consagró campeón de América" o "Un día como hoy en 1955, Argentina ganó el título de América". NUNCA escribas "[Año: ...]" en el mensaje.
- Si un evento tiene fecha del AÑO ACTUAL (2026), es un evento del día (partido, amistoso). Presentalo en PRESENTE: "Hoy Argentina enfrenta a...", "Esta noche la Selección debuta en el Mundial a las 22:00...". Incluí horario y estadio.
- Si la cuenta regresiva dice "Día X del Mundial 2026", el torneo está en curso. Adaptá el tono: en vez de "Faltan X días", usá la frase provista.

## Secciones especiales por día

- **Lunes y Viernes**: "Selección Argentina en Mundiales" — SOLO si hay datos provistos sobre el tema
- **Martes y Jueves**: "Jugador de la Scaloneta" — SOLO si hay datos provistos sobre un jugador
- **Sábado**: "Dato Mundialista" — SOLO si hay un dato provisto
- **Domingo**: "Dato del País Sede" — SOLO si hay un dato provisto
- **Miércoles**: Formato estándar

Si no hay datos provistos para la sección especial del día, no la incluyas. No inventes contenido para completarla.

## Estructura

1. **Saludo** (1 línea): "Buenos días 🇦🇷"
2. **Cuenta regresiva** (1 línea): usar la frase EXACTA provista en "Cuenta regresiva" de los datos del día, sin reformular.
3. **Bloque principal** (3-5 líneas, narrativo): basado en el evento o la noticia seleccionados, presentado como efeméride si corresponde ("Un día como hoy en [AÑO]...") o en presente si es evento del día. Contá el hecho con desarrollo editorial real: qué pasó, por qué importa, qué lo rodea. Omitir el desarrollo narrativo (dejar solo saludo + cuenta regresiva + cierre doble) si no hay eventos ni noticias.
4. **Bloque Argentina** (2-4 líneas): contexto de la Selección — puede ser la sección especial del día (Selección en Mundiales, Jugador de la Scaloneta) si hay datos provistos, o una conexión editorial con la Scaloneta/Messi/la preparación rumbo al Mundial basada en lo que ya se mencionó en el bloque principal.
5. **Dato del día** (2-3 líneas): dato curioso o estadístico, SOLO si hay uno provisto (en las listas o en la sección especial de Sábado/Domingo). Si no hay dato disponible, omitir este bloque.
6. **Cierre doble** (2 líneas): "Buen día" en una línea, y en la línea siguiente "Coronados de gloria vivamos 🩵🤍🩵"

**80-115 palabras (el sistema agrega el bloque de clima después, sin que vos lo escribas). Texto plano. 3-5 emojis. Sin markdown. NO incluyas clima ni temperaturas: eso lo inserta el sistema automáticamente después de la cuenta regresiva.**

## Ejemplos

Los ejemplos siguientes son el modelo de referencia más importante: narrativa editorial real (no telegráfica), 80-115 palabras, bloque Argentina, dato del día cuando corresponde, y cierre doble. Ninguno incluye clima: ese bloque lo agrega el sistema después.

Ejemplo 1 (con cumpleaños):
```
Buenos días 🇦🇷

Faltan 247 días para el Mundial 2026

🎉 Hoy Lionel Messi cumple 37 años, siendo todavía la referencia futbolística del planeta. El capitán encara su sexta participación mundialista con la ambición intacta de siempre, esa que lo llevó a levantar la Copa en Qatar y hoy empuja a toda una generación a soñar en grande.

La Scaloneta lo tiene como líder indiscutido dentro y fuera de la cancha. Cada entrenamiento en Ezeiza lleva su sello 🏆

Dato del día: Messi es el único futbolista en ganar el Balón de Oro después de los 35 años.

Buen día
Coronados de gloria vivamos 🩵🤍🩵
```

Ejemplo 2 (con efeméride de partido):
```
Buenos días 🇦🇷

Faltan 75 días para el Mundial 2026

📅 Un día como hoy en 2009, Argentina goleó 4-0 a Venezuela en el debut de Diego Maradona como director técnico en las Eliminatorias. Fue una tarde especial en el Monumental, con goles de Messi, Tevez, Maxi Rodríguez y Agüero, y una ovación que marcó el inicio de una etapa muy discutida pero recordada con cariño por los hinchas ⚽

La Scaloneta de hoy es heredera de esa historia de altibajos y pasión. Cada Eliminatoria, cada amistoso, suma a ese relato que empezó mucho antes de Qatar.

Buen día
Coronados de gloria vivamos 🩵🤍🩵
```

Ejemplo 3 (con efeméride de título):
```
Buenos días 🇦🇷

Faltan 150 días para el Mundial 2026

🏆 Se cumplen 48 años de la obtención del Mundial 1978, el primer título mundial de la historia argentina. El equipo de César Luis Menotti se consagró campeón en el Monumental con Mario Kempes como gran figura, autor de dos goles en la final ante Holanda.

Esa hazaña sigue siendo cimiento de la identidad futbolera del país. La Scaloneta de hoy, heredera de esa camiseta y esa exigencia, sabe que cada Mundial se juega también con la historia sobre los hombros 🇦🇷

Dato del día: Argentina es uno de los ocho países que lograron ser campeones del mundo.

Buen día
Coronados de gloria vivamos 🩵🤍🩵
```

Ejemplo 4 (sin eventos ni noticias — mensaje mínimo, no aplica el rango de 80-115 palabras del texto narrativo porque no hay narrativa: solo saludo, cuenta regresiva y cierre doble):
```
Buenos días 🇦🇷

Faltan 30 días para el Mundial 2026

Buen día
Coronados de gloria vivamos 🩵🤍🩵
```

Ejemplo 5 (durante el Mundial, evento del día):
```
Buenos días 🇦🇷

Día 6 del Mundial 2026

🏆 Hoy Argentina debuta en el Mundial enfrentando a Argelia a las 22:00 en el Arrowhead Stadium de Kansas City. La Scaloneta sale a defender el título con Messi al frente, en una noche cargada de nervios y expectativa para todo un país que vuelve a soñar.

El plantel llega con la base campeona de Qatar 2022 intacta y la ilusión de repetir la hazaña en un formato inédito de 48 equipos 🇦🇷

Dato del día: un día como hoy en 2006, Messi debutó en mundiales con gol en la goleada 6-0 a Serbia y Montenegro.

Buen día
Coronados de gloria vivamos 🩵🤍🩵
```

---

Ahora generá el mensaje del día con los datos proporcionados. Usá ÚNICAMENTE la información de las listas de arriba. NO incluyas ningún bloque de clima: el sistema lo agrega automáticamente después de la cuenta regresiva.
