# Formato de Eventos - events.json

Guía completa para agregar eventos a `data/events.json`.

## 📋 Estructura General

```json
{
  "description": "Estructura de eventos del día para InforMessi",
  "schema_version": "1.0",
  "events": [
    // Array de eventos
  ],
  "event_types": { /* tipos disponibles */ },
  "priorities": { /* niveles de prioridad */ }
}
```

---

## 🎯 Tipos de Eventos

### 1. `birthday` - Cumpleaños

```json
{
  "date": "2026-06-24",
  "type": "birthday",
  "priority": "high",
  "person": "Lionel Messi",
  "age": 39,
  "description": "Cumpleaños de Lionel Messi, capitán de la selección argentina"
}
```

**Campos requeridos:**
- `date`: Fecha en formato `YYYY-MM-DD`
- `type`: `"birthday"`
- `priority`: `"critical"`, `"high"`, `"medium"`, o `"low"`
- `person`: Nombre de la persona
- `age`: Edad que cumple
- `description`: Descripción del evento

---

### 2. `match` - Partido

```json
{
  "date": "2026-06-15",
  "type": "match",
  "priority": "critical",
  "opponent": "Brasil",
  "venue": "Estadio Azteca, México",
  "time": "20:00",
  "competition": "Mundial 2026 - Fase de Grupos",
  "description": "Argentina vs Brasil en el Estadio Azteca"
}
```

**Campos requeridos:**
- `date`: Fecha del partido
- `type`: `"match"`
- `priority`: Generalmente `"critical"` para partidos oficiales
- `opponent`: Rival
- `venue`: Estadio/ciudad
- `time`: Hora (formato `HH:MM`)
- `description`: Descripción breve

**Campos opcionales:**
- `competition`: Torneo/competencia
- `is_home`: `true`/`false` (si es local)

---

### 3. `historical` - Evento Histórico

```json
{
  "date": "2026-06-22",
  "type": "historical",
  "priority": "medium",
  "description": "1986: Diego Maradona marca el 'Gol del Siglo' contra Inglaterra en el Mundial de México",
  "historical_year": "1986",
  "source": "Wikipedia",
  "url": "https://es.wikipedia.org/wiki/22_de_junio"
}
```

**Campos requeridos:**
- `date`: Fecha en formato `YYYY-MM-DD` (para el año 2026)
- `type`: `"historical"`
- `priority`: Generalmente `"low"` o `"medium"`
- `description`: Descripción del evento histórico

**Campos opcionales:**
- `historical_year`: Año en que ocurrió el evento
- `source`: Fuente (ej: "Wikipedia")
- `url`: URL de referencia

---

### 4. `announcement` - Anuncio Oficial

```json
{
  "date": "2026-03-15",
  "type": "announcement",
  "priority": "high",
  "description": "Scaloni anuncia la lista de convocados para los amistosos de marzo",
  "source": "AFA",
  "url": "https://www.afa.com.ar/es/posts/lista-convocados"
}
```

**Campos requeridos:**
- `date`: Fecha del anuncio
- `type`: `"announcement"`
- `priority`: `"high"` o `"critical"` según importancia
- `description`: Descripción del anuncio

**Campos opcionales:**
- `source`: Fuente del anuncio (ej: "AFA", "FIFA")
- `url`: URL del anuncio

---

### 5. `patriotic` - Fecha Patria

```json
{
  "date": "2026-05-25",
  "type": "patriotic",
  "priority": "medium",
  "description": "Día de la Revolución de Mayo - Fecha patria argentina"
}
```

**Campos requeridos:**
- `date`: Fecha patria
- `type`: `"patriotic"`
- `priority`: Generalmente `"medium"`
- `description`: Descripción de la fecha patria

---

### 6. `news` - Noticia Relevante

```json
{
  "date": "2026-01-20",
  "type": "news",
  "priority": "high",
  "description": "Messi anuncia su continuidad en la selección hasta el Mundial 2026",
  "source": "TyC Sports",
  "url": "https://www.tycsports.com/messi-continua"
}
```

**Campos requeridos:**
- `date`: Fecha de la noticia
- `type`: `"news"`
- `priority`: Según relevancia
- `description`: Descripción de la noticia

**Campos opcionales:**
- `source`: Fuente de la noticia
- `url`: URL de la noticia

---

## 📊 Niveles de Prioridad

- **`critical`**: Máxima prioridad - el mensaje debe girar alrededor de esto
- **`high`**: Alta prioridad - debe estar en el bloque principal
- **`medium`**: Prioridad media - puede estar en bloque secundario
- **`low`**: Prioridad baja - mencionar si hay espacio

---

## 📝 Ejemplos Completos

### Ejemplo 1: Cumpleaños de Jugador

```json
{
  "date": "2026-02-14",
  "type": "birthday",
  "priority": "high",
  "person": "Ángel Di María",
  "age": 38,
  "description": "Cumpleaños de Ángel Di María, campeón del mundo en Qatar 2022"
}
```

### Ejemplo 2: Partido de Eliminatorias

```json
{
  "date": "2026-03-25",
  "type": "match",
  "priority": "critical",
  "opponent": "Brasil",
  "venue": "Estadio Monumental, Buenos Aires",
  "time": "21:00",
  "competition": "Eliminatorias Sudamericanas",
  "description": "Argentina vs Brasil en las Eliminatorias"
}
```

### Ejemplo 3: Aniversario Histórico

```json
{
  "date": "2026-12-18",
  "type": "historical",
  "priority": "high",
  "description": "2022: Argentina se consagra campeón del mundo en Qatar tras vencer a Francia en la final",
  "historical_year": "2022",
  "source": "Wikipedia"
}
```

### Ejemplo 4: Anuncio de Convocatoria

```json
{
  "date": "2026-05-20",
  "type": "announcement",
  "priority": "critical",
  "description": "Scaloni anuncia la lista definitiva de 26 jugadores para el Mundial 2026",
  "source": "AFA"
}
```

---

## 🔧 Cómo Agregar Eventos

### Método 1: Editar directamente `data/events.json`

1. Abre `data/events.json`
2. Agrega el evento al array `events`
3. Mantén el formato JSON válido
4. Guarda el archivo

**Ejemplo:**

```json
{
  "events": [
    // ... eventos existentes ...
    {
      "date": "2026-06-24",
      "type": "birthday",
      "priority": "high",
      "person": "Lionel Messi",
      "age": 39,
      "description": "Cumpleaños de Lionel Messi"
    }
  ]
}
```

### Método 2: Usar script de ayuda (futuro)

```bash
python3 scripts/add-event.py \
  --date 2026-06-24 \
  --type birthday \
  --person "Lionel Messi" \
  --age 39 \
  --priority high
```

---

## ✅ Validación

Antes de agregar eventos, verifica:

1. **Formato de fecha**: `YYYY-MM-DD` (ej: `2026-06-24`)
2. **Tipo válido**: Uno de los tipos definidos
3. **Prioridad válida**: `critical`, `high`, `medium`, o `low`
4. **JSON válido**: Usa un validador JSON si es necesario
5. **Campos requeridos**: Todos los campos requeridos están presentes

---

## 📅 Fechas Importantes para Agregar

- **Cumpleaños de jugadores**: Buscar fechas de nacimiento
- **Partidos oficiales**: Calendario de Eliminatorias, amistosos
- **Aniversarios históricos**: Mundiales anteriores, Copas América
- **Anuncios oficiales**: Listas de convocados, cambios técnicos
- **Fechas patrias**: 25 de Mayo, 9 de Julio, etc.

---

## 💡 Consejos

1. **Prioriza eventos relevantes**: No agregues eventos de baja relevancia
2. **Usa descripciones claras**: El LLM usará estas descripciones
3. **Mantén consistencia**: Sigue el formato de eventos existentes
4. **Verifica duplicados**: No agregues eventos que ya existen
5. **Actualiza regularmente**: Agrega eventos conforme se acercan fechas importantes

---

*Última actualización: 2025-12-28*

