# Scraper de Wikipedia - Eventos Históricos

Este documento explica cómo usar el scraper de Wikipedia para extraer eventos históricos y agregarlos a `events.json`.

## ¿Qué hace?

El scraper busca en Wikipedia eventos históricos de fútbol relacionados con Argentina y los formatea para agregar a `events.json`. Estos eventos se verifican cada día automáticamente.

## Uso Básico

### Scrapear un Mes Específico

```bash
source venv/bin/activate

# Scrapear diciembre (mes 12)
python3 scripts/scrape-wikipedia-events.py --month 12
```

### Scrapear Todos los Meses

```bash
# Esto puede tardar varios minutos
python3 scripts/scrape-wikipedia-events.py
```

### Dry Run (Ver sin Guardar)

```bash
# Ver qué eventos se encontrarían sin guardarlos
python3 scripts/scrape-wikipedia-events.py --month 6 --dry-run
```

## Fusionar con events.json

Para agregar los eventos scrapeados a `events.json`:

```bash
# Scrapear y fusionar automáticamente
python3 scripts/scrape-wikipedia-events.py --month 12 --merge
```

## Estructura de Eventos Generados

Los eventos se guardan en formato compatible con `events.json`:

```json
{
  "date": "2026-12-22",
  "type": "historical",
  "priority": "low",
  "description": "En 1986, Argentina ganó el Mundial...",
  "historical_year": "1986",
  "source": "Wikipedia",
  "url": "https://es.wikipedia.org/wiki/..."
}
```

**Nota**: La fecha usa el año 2026 (del Mundial), pero el mismo día/mes del evento histórico. El año histórico se guarda en `historical_year`.

## Verificación Diaria

Una vez agregados a `events.json`, los eventos se verifican automáticamente cada día:

```bash
# Recolectar datos del día (incluye eventos históricos)
python3 scripts/collect-daily-data.py --date 2026-12-22
```

Si hay eventos históricos para esa fecha, aparecerán en los datos recolectados.

## Ejemplo Completo

```bash
# 1. Scrapear eventos de diciembre
python3 scripts/scrape-wikipedia-events.py --month 12 --dry-run

# 2. Si los eventos son correctos, guardarlos y fusionar
python3 scripts/scrape-wikipedia-events.py --month 12 --merge

# 3. Verificar que se agregaron
cat data/events.json | python3 -m json.tool | grep -A 5 "2026-12"

# 4. Probar con una fecha específica
python3 scripts/collect-daily-data.py --date 2026-12-22
```

## Fuentes de Wikipedia

El scraper busca en:

- `Anexo:Hechos_relevantes_de_[mes]_en_el_fútbol` (ej: "Anexo:Hechos_relevantes_de_diciembre_en_el_fútbol")

## Filtrado

Solo se incluyen eventos que mencionen:
- Argentina, selección argentina
- Messi, Maradona
- Mundial, Copa América
- AFA, albiceleste, Scaloneta
- Y otras palabras clave relevantes

## Troubleshooting

### "No se encontraron eventos"

- Algunos meses pueden no tener eventos relevantes
- Verifica que la página de Wikipedia exista
- Prueba con meses conocidos (ej: junio, julio, diciembre)

### "Error al scrapear"

- Verifica conexión a internet
- Wikipedia puede bloquear requests muy frecuentes
- Espera unos minutos y vuelve a intentar

### "Eventos duplicados"

- El sistema evita duplicados automáticamente
- Si hay duplicados, revisa `events.json` manualmente

## Mejoras Futuras

- [ ] Cache de eventos scrapeados
- [ ] Validación de calidad de eventos
- [ ] Clasificación automática (títulos, partidos, etc.)
- [ ] Scraping incremental (solo nuevos eventos)

---

*Los eventos históricos enriquecen el contenido diario con contexto relevante*

