# Sistema de Memoria RAG - InforMessi

Sistema que evita repeticiones leyendo informes pasados y rastreando contenido ya usado.

## 🎯 Objetivo

Evitar que el LLM repita:
- Jugadores ya destacados
- Datos mundialistas ya mencionados
- Noticias ya cubiertas
- Eventos ya mencionados
- Frases y expresiones idénticas

## 🔧 Cómo Funciona

### 1. Análisis de Informes Pasados

El sistema lee los informes de los últimos 30 días (configurable) y extrae:
- **Secciones semanales usadas**: Qué tipo de sección se usó cada día
- **Jugadores mencionados**: Qué jugadores se destacaron y cuántas veces
- **Temas cubiertos**: Qué temas, eventos y noticias se mencionaron
- **Contenido específico**: Extractos de mensajes anteriores

### 2. Contexto para el LLM

Antes de generar un nuevo mensaje, el sistema proporciona al LLM:

```
### Memoria de Contenido Anterior (Evitar Repeticiones)

Se analizaron X informes anteriores.

**Sección del día: Jugador de la Scaloneta**

Jugadores ya destacados recientemente:
- Messi: 3 vez(es)
- Di María: 2 vez(es)
- Martínez: 1 vez(es)

💡 Prioriza jugadores que NO hayan sido destacados recientemente...
```

### 3. Selección Inteligente de Jugadores

Para las secciones de "Jugador de la Scaloneta" (Martes/Jueves):
- El sistema prioriza jugadores menos usados recientemente
- Si un jugador ya fue destacado, sugiere buscar un ángulo diferente

## 📋 Secciones Semanales con Memoria

### Lunes y Viernes: Selección en Mundiales
- Rastrea temas ya cubiertos (títulos, participaciones, momentos históricos)
- Sugiere variar el enfoque (si antes hablaste de 1986, ahora de 2022)

### Martes y Jueves: Jugador de la Scaloneta
- Rastrea qué jugadores se destacaron
- Prioriza jugadores no usados recientemente
- Si repite un jugador, sugiere un ángulo diferente

### Sábado: Dato Mundialista
- Rastrea datos ya compartidos
- Sugiere buscar nuevos ángulos (formato, sedes, récords)

### Domingo: Dato del País Sede
- Rastrea datos sobre países sede ya mencionados
- Sugiere variar entre Estados Unidos, Canadá y México

## 🧪 Probar el Sistema

### Ver qué información se extrae:

```bash
python3 scripts/rag_memory_system.py --date 2026-01-01
```

### Ver contexto generado para una fecha:

```bash
python3 scripts/rag_memory_system.py --date 2026-01-01 --days-back 30
```

### Generar un mensaje con memoria:

El sistema se integra automáticamente en `generate-message.py`. Solo genera un mensaje normalmente:

```bash
python3 scripts/generate-message.py --data data/daily-data.json
```

El contexto de memoria se incluirá automáticamente en el prompt.

## ⚙️ Configuración

### Días hacia atrás a analizar

Por defecto: 30 días

Cambiar en `generate-message.py`:
```python
memory_context = build_memory_context(data["date"], days_back=30)
```

### Ajustar sensibilidad

En `rag_memory_system.py`, puedes ajustar:
- `days_back`: Cuántos días hacia atrás analizar
- `max_reports`: Cuántos informes recientes considerar
- `players_used`: Umbral para considerar un jugador "muy usado"

## 📊 Información Rastreada

El sistema rastrea:

1. **Jugadores mencionados**: Cuántas veces cada jugador fue destacado
2. **Secciones por tipo**: Cuántas veces se usó cada tipo de sección
3. **Temas de noticias**: Títulos de noticias recientes
4. **Eventos mencionados**: Descripciones de eventos recientes
5. **Frases características**: Saludos y cierres usados

## 💡 Instrucciones al LLM

El sistema proporciona estas instrucciones al LLM:

- ✅ NO repetir exactamente la misma información, datos o frases
- ✅ Si mencionas algo similar, buscar un ángulo o enfoque diferente
- ✅ Variar el vocabulario y las expresiones
- ✅ Priorizar información nueva o perspectivas frescas
- ✅ Para jugadores: priorizar los menos usados recientemente

## 🔄 Integración Automática

El sistema se integra automáticamente en:

1. **`generate-message.py`**: Agrega contexto de memoria al prompt
2. **`generate-weekly-sections.py`**: Prioriza jugadores menos usados
3. **Flujo de generación**: Se ejecuta cada vez que se genera un mensaje

## 📈 Efectividad

El sistema mejora con el tiempo:
- Más informes pasados = mejor memoria
- Más variedad en las generaciones
- Menos repeticiones
- Contenido más fresco y diverso

## 🐛 Troubleshooting

### No encuentra informes pasados

- Verifica que existan archivos en `reports/`
- Verifica que los archivos tengan formato JSON válido
- Verifica que las fechas sean correctas (YYYY-MM-DD)

### Jugadores siempre repetidos

- Verifica que `data/players.json` tenga suficientes jugadores
- Aumenta `days_back` para analizar más historia
- Verifica que los informes pasados mencionen jugadores

### El contexto es muy largo

- Reduce `days_back` (ej: de 30 a 15 días)
- Reduce `max_reports` en `extract_recent_content()`

---

**El sistema de memoria garantiza contenido fresco y variado, evitando repeticiones molestas para los lectores.**

