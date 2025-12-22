# Scraper de Wikipedia - Guía Rápida

## ✅ Scraper Funcionando

El scraper mejorado (`scrape-wikipedia-events-v2.py`) ahora funciona correctamente.

### Problema Resuelto

- ❌ **Antes**: Buscaba páginas que no existen (`Anexo:Hechos_relevantes_de_[mes]_en_el_fútbol`)
- ✅ **Ahora**: Usa páginas de fechas específicas (`22_de_junio`, `18_de_diciembre`, etc.)

## 🚀 Uso Rápido

### Scrapear Todos los Meses (Recomendado)

```bash
source venv/bin/activate

# Scrapear todos los meses y fusionar con events.json
python3 scripts/scrape-wikipedia-events-v2.py --merge
```

**Tiempo estimado**: 15-20 minutos  
**Resultado esperado**: 200-500 eventos históricos relevantes

### Scrapear un Mes Específico

```bash
# Ejemplo: junio (mes 6)
python3 scripts/scrape-wikipedia-events-v2.py --month 6 --merge
```

### Scrapear un Día Específico

```bash
# Ejemplo: 22 de junio (gol de Maradona)
python3 scripts/scrape-wikipedia-events-v2.py --day 22 --month 6 --merge
```

### Ver sin Guardar (Dry Run)

```bash
python3 scripts/scrape-wikipedia-events-v2.py --month 6 --dry-run
```

## 📊 Resultados Esperados

- **Por día importante**: 2-5 eventos relevantes
- **Por mes**: 20-50 eventos relevantes  
- **Total (12 meses)**: 200-500 eventos históricos

## ✅ Verificar Eventos

```bash
# Ver cuántos eventos hay en events.json
python3 -c "import json; d=json.load(open('data/events.json')); print(f'Total: {len(d.get(\"events\", []))} eventos')"

# Ver eventos de una fecha específica
python3 scripts/fetch-events-enhanced.py --date 2026-06-22
```

## 🔍 Filtrado

El scraper incluye eventos que mencionan:
- ✅ Argentina + fútbol/mundial/copa
- ✅ Selección argentina
- ✅ Messi, Maradona
- ✅ Mundial, Copa América, FIFA

Excluye:
- ❌ Eventos históricos generales (guerras, fundaciones, etc.)
- ❌ Eventos que solo mencionan "Argentina" geográficamente

---

**💡 Tip**: Ejecuta `--merge` una vez para poblar `events.json`. Los eventos se verificarán automáticamente cada día.

