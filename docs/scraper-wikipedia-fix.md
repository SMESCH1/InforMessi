# Fix del Scraper de Wikipedia

## Problema Identificado

El scraper original buscaba páginas con formato:
- `Anexo:Hechos_relevantes_de_[mes]_en_el_fútbol`

**Estas páginas no existen** (devuelven 404).

## Solución Implementada

Nuevo scraper (`scrape-wikipedia-events-v2.py`) que:

1. **Usa páginas de fechas específicas**: `22_de_junio`, `18_de_diciembre`, etc.
2. **Filtrado mejorado**: Solo eventos realmente de fútbol/Argentina
3. **Optimización**: Scrapea días importantes primero (22, 18, 11, etc.)

## Uso

### Scrapear un Día Específico

```bash
source venv/bin/activate
python3 scripts/scrape-wikipedia-events-v2.py --day 22 --month 6 --dry-run
```

### Scrapear un Mes

```bash
python3 scripts/scrape-wikipedia-events-v2.py --month 6 --dry-run
```

### Scrapear Todos los Meses y Fusionar

```bash
# Scrapear todos (puede tardar 15-20 minutos)
python3 scripts/scrape-wikipedia-events-v2.py --merge

# Verificar
python3 -c "import json; d=json.load(open('data/events.json')); print(f'Eventos: {len(d.get(\"events\", []))}')"
```

## Filtrado

El scraper filtra eventos que:

✅ **Incluye**:
- Mencionan "Argentina", "Messi", "Maradona", "Mundial", "Copa América"
- Mencionan "fútbol" + contexto argentino/mundial
- Eventos históricos de fútbol relevantes

❌ **Excluye**:
- Eventos de guerra, batallas, terremotos (a menos que sean de fútbol)
- Eventos históricos generales sin relación con fútbol

## Resultados Esperados

- **Por día**: 1-5 eventos relevantes (en días importantes)
- **Por mes**: 20-50 eventos relevantes
- **Total (12 meses)**: 200-500 eventos históricos

---

*El nuevo scraper es más preciso y encuentra eventos realmente relevantes*

