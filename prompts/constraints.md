# Restricciones y Reglas de Contenido - InforMessi

Este documento detalla las restricciones técnicas y de contenido que deben aplicarse en la generación de mensajes.

## Restricciones de Contenido

### ❌ Prohibido Inventar Datos

- **Nunca** inventes fechas, estadísticas, resultados o información verificable
- Si no tienes un dato real, omítelo o usa una formulación genérica
- Ejemplo incorrecto: "Messi anotó 3 goles ayer" (si no es verdad)
- Ejemplo correcto: "Messi sigue siendo el máximo goleador histórico de la selección"

### ❌ Temas Prohibidos

1. **Política no deportiva**
   - No toques política general argentina o internacional
   - Solo política si está directamente ligada al fútbol (AFA, FIFA, decisiones técnicas)

2. **Violencia no deportiva**
   - No menciones violencia, tragedias o eventos trágicos no relacionados con fútbol
   - Si hay una tragedia relacionada con fútbol, trata el tema con respeto y mesura

3. **Personas privadas**
   - Enfócate en figuras públicas del fútbol
   - No menciones vida privada de jugadores, familiares o personas no públicas

4. **Humor interno contextual viejo**
   - No uses memes viejos o referencias que ya no aplican
   - El humor debe ser actual y contextual

### ❌ Clima y meteorología

- **No incluyas** temperatura, pronóstico, estado del tiempo ni ninguna sección de clima en el mensaje.

### ❌ Estilo Prohibido

- **No publicitario**: No promociones marcas, productos o servicios
- **No sensacionalista**: No exageres ni uses clickbait
- **No chatbot**: No uses frases como "Soy tu asistente" o "Te traigo"
- **No exagerado**: Mantén un tono mesurado y profesional

## Reglas de Priorización

### Orden de Prioridad para el Bloque Principal

1. **Evento importante del día** (máxima prioridad)
   - Cumpleaños de jugador clave (Messi, Di María, etc.)
   - Partido oficial de la selección
   - Anuncio oficial (lista, convocatoria, etc.)
   - Definición de grupos o sorteos

2. **Noticia relevante del día**
   - Anuncios de la AFA o FIFA
   - Lesiones o recuperaciones importantes
   - Transferencias relevantes de jugadores de la selección
   - Eventos históricos del fútbol argentino

3. **Formato estándar** (si no hay nada especial)
   - Dato interesante del Mundial
   - Información sobre preparación de la selección
   - Estadística o curiosidad mundialista

### Reglas de Eventos

- Los eventos deben venir estructurados (JSON) para que el LLM no "decida solo"
- Si hay múltiples eventos, priorizar por relevancia:
  1. Eventos oficiales (partidos, listas, sorteos)
  2. Cumpleaños de jugadores clave
  3. Aniversarios históricos
  4. Noticias relevantes

## Restricciones Técnicas

### Longitud

- **Mínimo**: 90 palabras
- **Máximo**: 130 palabras
- **Ideal**: 100-120 palabras

### Formato

- **Texto plano**: Sin markdown, sin HTML, sin código
- **Emojis**: Usar con moderación (🇦🇷, 🌤, ⚽)
- **Líneas**: Separar bloques con líneas en blanco
- **Listas**: Evitar listas con viñetas, usar texto corrido

### Estructura

- **7 bloques obligatorios**: Todos deben estar presentes
- **Orden flexible**: Puede variar según el contenido, pero mantener lógica
- **Cierre ritual**: Siempre terminar con "Coronados de gloria vivamos"

## Reglas de Visuales

### Imágenes

- **1 imagen o GIF por mensaje** (rol secundario, no protagonista)
- **Relacionada con**: Selección argentina, jugador, Mundial
- **No saturar**: La imagen complementa, no domina

### Fuentes de Imágenes

- Generadas por IA
- Banco de imágenes curado
- Reutilización inteligente (no repetir la misma imagen seguido)
- Assets propios (`assets/memes/` y `assets/media/`)

### Restricciones de Imágenes

- No usar imágenes de personas privadas
- No usar imágenes políticas o violentas
- Priorizar imágenes relacionadas con el contenido del mensaje

## Reglas de Memes

### Cuándo Usar Memes

- **Solo si es relevante**: El meme debe estar relacionado con el contenido del día
- **Actuales**: No usar memes viejos o referencias que ya no aplican
- **Contextual**: Debe sumar al mensaje, no distraer
- **Moderación**: Usar con criterio editorial, no saturar

### Cuándo NO Usar Memes

- Si el meme es viejo o ya no aplica
- Si fuerza una conexión artificial con el contenido
- Si puede ser ofensivo o inapropiado
- Si distrae del mensaje principal
- Si no hay un meme relevante disponible

### Fuentes de Memes

- Carpeta `assets/memes/` (memes curados)
- Memes actuales de la cultura futbolera argentina
- Solo si son parte del contexto del día

## Reglas de Material Audiovisual

### Material Disponible

- **Historia de la selección**: Momentos históricos, jugadores icónicos, mundiales anteriores
- **Noticias**: Anuncios oficiales, partidos importantes, eventos relevantes
- **Datos y estadísticas**: Infografías, datos curiosos, comparativas

### Cuándo Usar

- Cuando complementa el contenido del día
- Cuando aporta contexto histórico relevante
- Cuando enriquece el mensaje sin distraer

### Restricciones

- **Rol secundario**: El material complementa, no domina
- **Relevancia**: Debe estar relacionado con el contenido del día
- **Derechos**: Respetar derechos de autor, usar material con licencia apropiada
- **No saturar**: Usar con moderación

### Fuentes

- Carpeta `assets/media/` (material curado)
- Material relacionado con historia, noticias y datos de la selección

## Reglas de Reutilización

### Contenido

- El mensaje debe ser **reutilizable** en Telegram
- Debe poder **adaptarse** a X (Twitter) e Instagram
- Mantener formato que funcione en múltiples plataformas

### Adaptación

- Telegram: Formato completo
- X: Puede requerir acortar o dividir en hilos
- Instagram: Puede requerir ajustes visuales

## Validación Pre-Publicación

Antes de publicar, verificar:

- [ ] No hay datos inventados
- [ ] No hay temas prohibidos
- [ ] Longitud entre 90-130 palabras
- [ ] Estructura completa (7 bloques)
- [ ] Cierre ritual presente
- [ ] Tono editorial argentino
- [ ] No es publicitario ni sensacionalista
- [ ] Eventos priorizados correctamente

## Excepciones

Si un evento es tan importante que requiere modificar la estructura:

- **Permitido**: Ajustar el orden de bloques
- **Permitido**: Extender ligeramente el bloque principal (máximo 150 palabras totales)
- **No permitido**: Omitir bloques obligatorios
- **No permitido**: Cambiar el tono o estilo

---

**Estas restricciones son fundamentales para mantener la calidad y coherencia del proyecto.**

