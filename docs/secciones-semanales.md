# Secciones Semanales - InforMessi

Este documento explica el sistema de secciones especiales por día de la semana, basado en Informesch.

## Estructura Semanal

Basado en Informesch, algunos días de la semana tienen secciones especiales:

| Día | Sección | Descripción |
|-----|---------|-------------|
| **Lunes** | Selección Argentina en Mundiales | Historia, participaciones, títulos, momentos destacados |
| **Martes** | Jugador de la Scaloneta | Análisis o información sobre un jugador |
| **Miércoles** | Estándar | Formato normal sin sección especial |
| **Jueves** | Jugador de la Scaloneta | Análisis o información sobre un jugador |
| **Viernes** | Selección Argentina en Mundiales | Historia, participaciones, títulos, momentos destacados |
| **Sábado** | Dato Mundialista | Curiosidades, estadísticas, historia de los Mundiales |
| **Domingo** | Dato del País Sede | Información sobre Estados Unidos, Canadá, México (2026) |

## Implementación

### Generación Automática

Las secciones se generan automáticamente según el día de la semana en `generate-message.py`:

```python
from generate_weekly_sections import build_weekly_section_prompt
weekly_section = build_weekly_section_prompt(data["date"])
```

### Integración en el Prompt

La sección especial se agrega al prompt del LLM, que debe integrarla naturalmente en el mensaje (no como bloque separado).

## Ejemplos

### Lunes/Viernes: Selección Argentina en Mundiales

**Prompt generado**:
```
### Sección Especial del Día (Selección Argentina en Mundiales)

Incluye una sección sobre la historia de la selección argentina en los Mundiales. 
Puedes mencionar participaciones históricas, títulos, momentos destacados, 
o comparar con la preparación actual para 2026.
```

**Ejemplo de mensaje**:
```
Buenos días 🇦🇷

Faltan 171 días para el Mundial 2026.

La selección argentina tiene una rica historia en los Mundiales, con tres títulos 
(1978, 1986, 2022) y múltiples participaciones destacadas. En 2026 buscará defender 
el título en un formato expandido a 48 equipos.

La Scaloneta continúa su preparación...
```

### Martes/Jueves: Jugador de la Scaloneta

**Prompt generado**:
```
### Sección Especial del Día (Jugador de la Scaloneta)

Incluye una sección destacando un jugador de la Scaloneta. Puede ser un jugador clave, 
alguien que esté en buen momento, o información relevante sobre algún integrante del plantel actual.

**Jugador sugerido**: Lionel Messi (Delantero, Inter Miami)
```

**Ejemplo de mensaje**:
```
Buenos días 🇦🇷

Faltan 171 días para el Mundial 2026.

Lionel Messi, capitán de la Scaloneta, continúa siendo la referencia mundial del fútbol. 
A sus 37 años, prepara su sexta participación en un Mundial, buscando defender el título 
obtenido en Qatar 2022.

La selección argentina...
```

### Sábado: Dato Mundialista

**Prompt generado**:
```
### Sección Especial del Día (Dato Mundialista)

Incluye un dato mundialista destacado. Puede ser sobre la historia de los Mundiales, 
estadísticas, curiosidades, o información relevante sobre el formato, sedes, o equipos participantes.
```

### Domingo: Dato del País Sede

**Prompt generado**:
```
### Sección Especial del Día (Dato del País Sede)

Incluye un dato sobre los países sede del Mundial 2026 (Estados Unidos, Canadá, México). 
Puede ser información sobre las ciudades, estadios, cultura futbolera, o curiosidades 
de estos países relacionados con el Mundial.
```

## Configuración de Jugadores

Los jugadores para las secciones de Martes/Jueves se configuran en `data/players.json`:

```json
{
  "players": [
    {
      "name": "Lionel Messi",
      "position": "Delantero",
      "club": "Inter Miami",
      "age": 37,
      "notes": "Capitán, máximo goleador histórico"
    }
  ]
}
```

El sistema selecciona un jugador aleatorio o según alguna lógica para cada día.

## Personalización

### Cambiar Días de Secciones

Edita `scripts/generate-weekly-sections.py`, función `get_weekday_section()`:

```python
sections = {
    0: {  # Lunes
        "type": "seleccion_mundiales",
        # ...
    },
    # ...
}
```

### Agregar Nuevas Secciones

1. Agrega el tipo en `get_weekday_section()`
2. Actualiza el prompt en `main-editorial.md`
3. Agrega lógica específica si es necesario

## Testing

Probar secciones semanales:

```bash
source venv/bin/activate

# Ver qué sección corresponde a una fecha
python3 scripts/generate-weekly-sections.py --date 2025-12-22  # Lunes
python3 scripts/generate-weekly-sections.py --date 2025-12-23  # Martes
```

---

*Las secciones especiales enriquecen el contenido y mantienen la variedad del mensaje diario*

