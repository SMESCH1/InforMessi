# Scraper de Eventos Históricos - InforMessi

Este documento explica cómo usar el scraper de eventos históricos para obtener fechas, aniversarios y datos del día.

## ¿Qué hace el scraper?

El scraper obtiene eventos históricos de fútbol que ocurrieron en la misma fecha (día/mes) en años anteriores. Estos eventos se usan para:

- **Fechas históricas**: Aniversarios de partidos importantes, títulos, etc.
- **Datos del día**: Información interesante sobre la historia del fútbol argentino
- **Contexto**: Enriquecer el mensaje diario con datos históricos relevantes

## Fuentes Disponibles

### 1. Wikipedia (Automático)

El scraper busca automáticamente en Wikipedia:
- Páginas de "Hechos relevantes de [mes] en el fútbol"
- Páginas específicas de la fecha

**No requiere configuración**, funciona automáticamente.

### 2. Sitios Personalizados (Configurables)

Puedes agregar tus propios sitios web editando `data/scrape-config.json`.

## Configurar Sitios Personalizados

### Paso 1: Editar `data/scrape-config.json`

```json
{
  "sites": [
    {
      "name": "TyC Sports Historia",
      "url": "https://www.tycsports.com/futbol/historia",
      "enabled": true,
      "selectors": {
        "container": "article",
        "title": "h2",
        "description": "p",
        "date": ".date"
      }
    }
  ]
}
```

### Paso 2: Encontrar los Selectores CSS

1. Abre el sitio web en tu navegador
2. Inspecciona el HTML (F12)
3. Identifica:
   - **Container**: El elemento que contiene cada evento/artículo
   - **Title**: El título del evento
   - **Description**: La descripción o texto del evento
   - **Date**: (Opcional) La fecha del evento

### Paso 3: Probar

```bash
source venv/bin/activate
python3 scripts/scrape-events.py --date 2024-12-22
```

## Uso del Scraper

### Uso Básico (Wikipedia)

```bash
source venv/bin/activate
python3 scripts/scrape-events.py
```

### Con URL Personalizada

```bash
python3 scripts/scrape-events.py \
  --url "https://ejemplo.com/historia" \
  --container "div.article" \
  --title "h2"
```

### Guardar Resultados

```bash
python3 scripts/scrape-events.py --output /tmp/eventos-hoy.json
```

## Integración Automática

El scraper se ejecuta automáticamente cuando usas:

```bash
python3 scripts/fetch-events-enhanced.py
```

O cuando recolectas todos los datos:

```bash
python3 scripts/collect-daily-data.py --output datos.json
```

## Estructura de Eventos Obtenidos

```json
{
  "date": "2024-12-22",
  "type": "historical",
  "priority": "low",
  "description": "En 1986, Argentina ganó el Mundial...",
  "year": "1986",
  "source": "Wikipedia",
  "url": "https://..."
}
```

## Ejemplos de Uso

### Ejemplo 1: Scraper de Wikipedia

```bash
# Obtener eventos históricos del día de hoy
python3 scripts/scrape-events.py
```

### Ejemplo 2: Scraper Personalizado

```bash
# Scrapear un sitio específico
python3 scripts/scrape-events.py \
  --url "https://www.tycsports.com/futbol/historia" \
  --container "article" \
  --title "h2" \
  --output eventos.json
```

### Ejemplo 3: Integrado en el Flujo

Los eventos históricos se integran automáticamente en `fetch-events-enhanced.py` y se usan en la generación de mensajes.

## Troubleshooting

### "No se encontraron eventos"

- Verifica que la fecha sea correcta
- Algunos días pueden no tener eventos históricos relevantes
- Prueba con fechas conocidas (ej: 22 de junio, día del gol de Maradona)

### "Error al scrapear"

- Verifica que el sitio web esté accesible
- Los selectores CSS pueden haber cambiado
- Algunos sitios bloquean scrapers (usa headers apropiados)

### Selectores no funcionan

- Los sitios web cambian su estructura
- Usa herramientas de desarrollo del navegador para encontrar selectores actuales
- Prueba selectores más generales (ej: `article` en lugar de `div.article.specific`)

## Mejoras Futuras

- [ ] Cache de eventos históricos (no scrapear lo mismo cada día)
- [ ] Más fuentes automáticas
- [ ] Validación de eventos duplicados
- [ ] Clasificación automática de eventos (títulos, partidos, etc.)

---

*El scraper ayuda a enriquecer los mensajes con contexto histórico relevante*

