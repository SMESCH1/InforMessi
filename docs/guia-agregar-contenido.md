# Guía: Agregar Contenido a InforMessi

Esta guía explica cómo agregar eventos, contenido audiovisual y noticias manuales al sistema.

---

## 📅 Agregar Eventos

Los eventos se almacenan en `data/events.json` y se incluyen automáticamente en los informes del día correspondiente.

### Formato de Eventos

```json
{
  "date": "2026-01-15",
  "type": "birthday",
  "priority": "high",
  "person": "Lionel Messi",
  "age": 37,
  "description": "Cumpleaños de Lionel Messi"
}
```

### Tipos de Eventos

#### 1. Cumpleaños (`birthday`)

```json
{
  "date": "2026-06-24",
  "type": "birthday",
  "priority": "high",
  "person": "Lionel Messi",
  "age": 38,
  "description": "Cumpleaños de Lionel Messi"
}
```

**Campos:**
- `date`: Fecha en formato `YYYY-MM-DD`
- `type`: `"birthday"`
- `priority`: `"high"` (siempre para cumpleaños importantes)
- `person`: Nombre de la persona
- `age`: Edad que cumple
- `description`: Descripción breve

#### 2. Eventos Históricos (`historical`)

```json
{
  "date": "2026-06-11",
  "type": "historical",
  "priority": "low",
  "description": "1978: Argentina gana su primer Mundial en casa",
  "historical_year": "1978",
  "source": "Wikipedia",
  "url": "https://es.wikipedia.org/wiki/11_de_junio"
}
```

**Campos:**
- `date`: Fecha en formato `YYYY-MM-DD`
- `type`: `"historical"`
- `priority`: `"low"` o `"medium"` (raramente `"high"`)
- `description`: Descripción del evento histórico
- `historical_year`: Año del evento
- `source`: Fuente (opcional)
- `url`: URL de referencia (opcional)

#### 3. Partidos (`match`)

```json
{
  "date": "2026-06-15",
  "type": "match",
  "priority": "high",
  "description": "Argentina vs Brasil - Amistoso",
  "venue": "Estadio Monumental",
  "time": "20:00"
}
```

**Campos:**
- `date`: Fecha en formato `YYYY-MM-DD`
- `type`: `"match"`
- `priority`: `"high"` para partidos importantes
- `description`: Descripción del partido
- `venue`: Estadio (opcional)
- `time`: Hora (opcional)

### Cómo Agregar Eventos

1. **Abre el archivo:**
   ```bash
   nano data/events.json
   # O usa tu editor preferido
   ```

2. **Agrega el evento** en el array `events`:
   ```json
   {
     "description": "...",
     "schema_version": "1.0",
     "events": [
       // ... eventos existentes ...
       {
         "date": "2026-01-15",
         "type": "birthday",
         "priority": "high",
         "person": "Nuevo Jugador",
         "age": 25,
         "description": "Cumpleaños de Nuevo Jugador"
       }
     ]
   }
   ```

3. **Guarda el archivo**

4. **Verifica el formato:**
   ```bash
   python3 -c "import json; json.load(open('data/events.json'))"
   ```

### Prioridades

- **`high`**: Eventos muy importantes (cumpleaños de Messi, partidos importantes)
- **`medium`**: Eventos relevantes (cumpleaños de otros jugadores, eventos históricos importantes)
- **`low`**: Eventos menores (eventos históricos generales)

---

## 🎬 Agregar Contenido Audiovisual

El contenido audiovisual se detecta automáticamente si está en la carpeta correcta.

### Estructura de Carpetas

```
assets/
└── media/
    └── YYYY-MM-DD/          # Fecha del informe
        ├── imagen1.jpg
        ├── imagen2.png
        ├── video1.mp4
        └── ...
```

### Formatos Soportados

**Imágenes:**
- `.jpg`, `.jpeg`
- `.png`
- `.gif`
- `.webp`

**Videos:**
- `.mp4`
- `.mov`

### Cómo Agregar Media

1. **Crea la carpeta** para la fecha:
   ```bash
   mkdir -p assets/media/2026-01-15
   ```

2. **Copia los archivos** a la carpeta:
   ```bash
   cp mi-imagen.jpg assets/media/2026-01-15/
   ```

3. **El sistema detectará automáticamente** el contenido al generar/actualizar el informe

### Prioridad de Imágenes

Si hay múltiples imágenes, el sistema usa la primera encontrada como imagen principal.

**Recomendación:** Nombra la imagen principal como `01.jpg` o `principal.jpg` para que sea la primera.

---

## 📰 Agregar Noticias Manuales

Las noticias normalmente se obtienen automáticamente de NewsAPI y Reddit, pero puedes agregar noticias manuales.

### Formato de Noticias

Las noticias se agregan directamente en el informe JSON:

```json
{
  "date": "2025-12-31",
  "data": {
    "news": [
      {
        "title": "Título de la noticia",
        "description": "Descripción breve",
        "url": "https://ejemplo.com/noticia",
        "source": "Fuente Manual",
        "published_at": "2025-12-31T10:00:00"
      }
    ]
  }
}
```

### Cómo Agregar Noticias Manuales

1. **Abre el informe:**
   ```bash
   nano reports/2025-12-31.json
   ```

2. **Agrega la noticia** en el array `data.news`:
   ```json
   {
     "data": {
       "news": [
         // ... noticias existentes ...
         {
           "title": "Nueva noticia importante",
           "description": "Descripción de la noticia",
           "url": "https://ejemplo.com",
           "source": "Fuente Manual",
           "published_at": "2025-12-31T10:00:00"
         }
       ]
     }
   }
   ```

3. **Guarda el archivo**

4. **Actualiza el informe** para regenerar el mensaje:
   ```bash
   python3 scripts/update-today-report.py --date 2025-12-31
   ```

---

## 📋 Checklist de Agregar Contenido

### Para un Día Específico

- [ ] **Eventos:** Agregados en `data/events.json`
- [ ] **Media:** Archivos en `assets/media/YYYY-MM-DD/`
- [ ] **Noticias:** Agregadas manualmente en el informe (si es necesario)

### Verificación

1. **Verifica eventos:**
   ```bash
   python3 -c "import json; e=json.load(open('data/events.json')); print([x for x in e['events'] if x['date']=='2026-01-15'])"
   ```

2. **Verifica media:**
   ```bash
   ls -la assets/media/2026-01-15/
   ```

3. **Regenera el informe:**
   ```bash
   python3 scripts/update-today-report.py --date 2026-01-15
   ```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Agregar Cumpleaños

```json
{
  "date": "2026-06-24",
  "type": "birthday",
  "priority": "high",
  "person": "Lionel Messi",
  "age": 39,
  "description": "Cumpleaños de Lionel Messi"
}
```

### Ejemplo 2: Agregar Evento Histórico

```json
{
  "date": "2026-07-13",
  "type": "historical",
  "priority": "medium",
  "description": "2014: Alemania gana el Mundial en Brasil",
  "historical_year": "2014",
  "source": "Wikipedia"
}
```

### Ejemplo 3: Agregar Media

```bash
# Crear carpeta
mkdir -p assets/media/2026-06-24

# Agregar imagen
cp messi-birthday.jpg assets/media/2026-06-24/

# El sistema la detectará automáticamente
```

---

## ⚠️ Notas Importantes

1. **Formato de fechas:** Siempre `YYYY-MM-DD`
2. **JSON válido:** Verifica que el JSON sea válido antes de guardar
3. **Backup:** Haz backup de `data/events.json` antes de editar
4. **Media:** Los archivos grandes pueden ralentizar el proceso
5. **Noticias:** Las noticias manuales se mezclan con las automáticas

---

## 🔄 Actualizar Informes con Nuevo Contenido

Después de agregar contenido:

```bash
# Actualizar informe específico
python3 scripts/update-today-report.py --date 2026-01-15

# O regenerar desde cero
python3 scripts/generate-advance-reports.py --days 1 --start-date 2026-01-15
```

El sistema:
1. Detectará los nuevos eventos
2. Incluirá el contenido audiovisual
3. Regenerará el mensaje con el nuevo contenido

