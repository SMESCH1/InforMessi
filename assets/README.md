# Assets - InforMessi

Este directorio contiene recursos visuales y audiovisuales para enriquecer los mensajes diarios.

## Estructura

```
assets/
├── memes/          # Memes de fútbol argentino
├── media/          # Material audiovisual (historia, noticias, datos)
└── README.md       # Este archivo
```

## Memes (`memes/`)

### Propósito

Memes de fútbol argentino que pueden usarse para complementar mensajes cuando son relevantes y actuales.

### Reglas de Uso

- **Solo si es relevante**: El meme debe estar relacionado con el contenido del mensaje del día
- **Actuales**: No usar memes viejos o referencias que ya no aplican
- **Moderación**: No saturar, usar con criterio editorial
- **Contextual**: Debe sumar al mensaje, no distraer

### Cuándo Usar

- Cuando hay un evento importante que tiene un meme asociado conocido
- Cuando el meme complementa el tono del mensaje sin forzarlo
- Cuando es parte de la cultura futbolera argentina actual

### Cuándo NO Usar

- Si el meme es viejo o ya no aplica
- Si fuerza una conexión artificial con el contenido
- Si puede ser ofensivo o inapropiado
- Si distrae del mensaje principal

### Formato

- Imágenes: `.jpg`, `.png`, `.gif`
- Nombres descriptivos: `meme-messi-mundial-2026.jpg`
- Organización por tema o fecha si es necesario

## Material Audiovisual (`media/`)

### Propósito

Material relacionado con:
- Historia de la selección argentina
- Noticias relevantes
- Datos y estadísticas
- Momentos históricos mundialistas

### Tipos de Contenido

1. **Historia de la Selección**
   - Momentos históricos
   - Jugadores icónicos
   - Mundiales anteriores

2. **Noticias**
   - Anuncios oficiales
   - Partidos importantes
   - Eventos relevantes

3. **Datos y Estadísticas**
   - Infografías
   - Datos curiosos
   - Comparativas

### Reglas de Uso

- **Rol secundario**: El material complementa, no domina
- **Relevancia**: Debe estar relacionado con el contenido del día
- **Calidad**: Material curado, no saturar
- **Derechos**: Respetar derechos de autor, usar material con licencia apropiada

### Formato

- Imágenes: `.jpg`, `.png`
- Videos: `.mp4` (si se usan)
- GIFs: `.gif`
- Nombres descriptivos: `historia-seleccion-1986.jpg`

## Integración con Mensajes

### En el Prompt

El LLM puede referenciar estos recursos cuando:
- Son relevantes al contenido del día
- Complementan el mensaje sin distraer
- Mantienen el tono editorial

## Mantenimiento

### Agregar Nuevos Assets

1. Colocar archivo en carpeta correspondiente (`memes/` o `media/`)
2. Usar nombre descriptivo
3. Documentar si es necesario (en este README o archivo separado)

### Organización

- Por tema (jugadores, mundiales, etc.)
- Por fecha (si es relevante)
- Por tipo de contenido

### Actualización

- Revisar periódicamente memes obsoletos
- Actualizar material según eventos actuales
- Mantener calidad y relevancia

---

*Los assets se detectan automáticamente por el script `detect-media.py` al generar el informe diario.*

