# Prompt Principal - Generación Diaria

## Contexto del Día

A continuación recibirás la información del día para generar el mensaje:

### Datos del Día
- **Fecha**: [FECHA]
- **Días restantes al Mundial 2026**: [X días]

### Eventos del Día
[Lista de eventos relevantes: cumpleaños, partidos, anuncios, etc.]

### Noticias Relevantes
[Noticias del día relacionadas con fútbol, selección argentina, Mundial]

---

## Instrucciones

Genera un mensaje informativo diario siguiendo estas especificaciones:

### ⚠️ Regla crítica de uso de datos

- Si hay eventos, el **bloque principal** DEBE girar alrededor de un evento de la lista.
- Si no hay eventos pero sí noticias, el **bloque principal** DEBE basarse en al menos 1 noticia de la lista.
- **NUNCA** inventes noticias, convocatorias, anuncios, lesiones ni datos que no estén en las listas provistas.
- Si ambas listas están vacías, genera un mensaje corto con solo saludo, cuenta regresiva y cierre. No agregues bloques de contenido inventado.

### Secciones Especiales por Día de la Semana

Algunos días de la semana tienen secciones especiales que deben incluirse:

- **Lunes y Viernes**: Sección sobre "Selección Argentina en Mundiales" (historia, participaciones, títulos, momentos destacados)
- **Martes y Jueves**: Sección sobre "Jugador de la Scaloneta" (análisis, información, momento actual de un jugador)
- **Sábado**: Sección "Dato Mundialista" (curiosidades, estadísticas, historia de los Mundiales)
- **Domingo**: Sección "Dato del País Sede" (información sobre Estados Unidos, Canadá, México - países sede 2026)
- **Miércoles**: Formato estándar sin sección especial

Estas secciones deben integrarse naturalmente en el mensaje, no como bloques separados.

### Estructura Requerida

1. **Saludo** (1 línea)
   - Ejemplo: "Buenos días 🇦🇷"

2. **Cuenta regresiva** (1 línea)
   - Ejemplo: "Faltan X días para el Mundial 2026"

3. **Bloque principal del día** (3-5 líneas)
   - Si hay evento importante (cumpleaños de jugador, partido, anuncio oficial): este bloque debe girar alrededor de eso
   - Si no hay evento importante: usa formato estándar con noticia relevante o dato interesante

5. **Bloque Argentina** (2-4 líneas)
   - Selección argentina
   - Jugador destacado
   - Historia mundialista
   - Scaloneta
   - SOLO incluir si existe un dato concreto en las listas del día
   - No usar frases genéricas ni repetidas (ej: "La selección argentina continúa su preparación...")
   - (Priorizar si hay algo relevante del día)
   - Si no hay dato concreto, omitir este bloque
   

6. **Dato del día** (2-3 líneas)
   - Mundial 2026
   - País sede
   - Cultura futbolera
   - Estadística interesante
   - ⚠️ PROHIBIDO repetir datos que aparezcan en la sección "Datos del día YA PUBLICADOS" de la memoria
   - Si todos los datos disponibles ya fueron publicados, OMITIR esta sección por completo

7. **Cierre** (2 líneas)
   - "Coronados de gloria vivamos"

### Longitud

- **Objetivo**: 90-130 palabras
- **Formato**: Texto plano, sin markdown
- **Emojis**: Usar emojis relevantes y variados para hacer el mensaje más atractivo y visual:
  - 🇦🇷 (bandera Argentina) - en saludo o cierre
  - ⚽ (fútbol) - para mencionar partidos, jugadores, fútbol en general
  - 🏆 (trofeo) - para títulos, logros, campeonatos
  - 🎉 (celebración) - para cumpleaños, aniversarios, logros
  - 📅 (calendario) - para fechas importantes
  - ⭐ (estrella) - para jugadores destacados, momentos especiales
  - 🔥 (fuego) - para momentos emocionantes, actuaciones destacadas
  - 💪 (fuerza) - para esfuerzo, preparación, determinación
  - 🌍 (mundo) - para Mundial, países, sedes
  - ⚡ (rayo) - para velocidad, acción, dinamismo
  - 🎯 (objetivo) - para metas, objetivos, preparación
  - 🩵 (corazón celeste) - para pasión, amor por la selección
  - 🤍 (corazón blanco) - para pasión, amor por la selección
  - 📊 (gráfico) - para estadísticas, datos
  - 🚀 (cohete) - para progreso, avance, futuro
  - Usa 3-5 emojis por mensaje, distribuidos estratégicamente para mejorar la lectura

### Priorización

1. Si hay **evento importante** (cumpleaños de jugador clave, partido oficial, anuncio de lista): el mensaje debe centrarse en eso
2. Si hay **noticia relevante** del día: incluirla en el bloque principal
3. Si no hay nada especial: usar formato estándar con datos interesantes

### Recursos Disponibles

- **Memes de fútbol argentino**: Disponibles en carpeta de assets (usar con moderación y solo si son relevantes)
- **Material audiovisual**: Historia de la selección, noticias, datos (usar para contexto, no como protagonista)

### Restricciones

- No inventar datos
- No mencionar personas privadas
- No tocar política o violencia no deportiva
- No usar humor interno contextual viejo
- No ser publicitario
- Memes: Solo usar si son actuales y relevantes al contenido del día

### Formato de Salida

Genera SOLO el texto del mensaje, sin explicaciones adicionales, sin markdown, sin código. El texto debe estar listo para publicar.

---

## Ejemplos de Salida Esperada

### Ejemplo 1 (solo formato de referencia)
```
Buenos días 🇦🇷

Faltan 247 días para el Mundial 2026 ⚽

🎉 [Evento del día basado en los datos provistos]

📊 Dato del día: [Dato ÚNICO extraído de las listas o la sección semanal, NUNCA repetido de días anteriores]

Coronados de gloria vivamos 🩵🤍🩵
```
### Ejemplo 2 (solo formato de referencia)
```
Buenos días 🇦🇷

Faltan 150 días para el Mundial 2026 ⚽

🎉 [Aniversario o cumpleaños basado en la lista de eventos del día]

📊 Dato del día: [Estadística verificable diferente a las listadas en la memoria de contenido anterior]

Coronados de gloria vivamos 🩵🤍🩵
```

**IMPORTANTE**: Los ejemplos son SOLO referencia de formato y estructura. NUNCA copies un dato, frase o estadística de un ejemplo. Usa ÚNICAMENTE datos de las listas de eventos/noticias del día y de la sección de memoria proporcionadas.

---

**Ahora genera el mensaje del día con los datos proporcionados.**

