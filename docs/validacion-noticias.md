# Validación de Noticias - InforMessi

Este documento explica cómo funciona la validación de noticias para evitar información obsoleta o desactualizada.

## Problema Resuelto

**Antes**: Las noticias podían contener información obsoleta (ej: mencionar a Gerardo Martino como entrenador actual).

**Ahora**: Las noticias se validan por:
1. **Fecha**: Solo noticias de los últimos 3 días
2. **Contenido**: Filtrado de información obsoleta

## Validaciones Aplicadas

### 1. Validación por Fecha

Solo se aceptan noticias publicadas en:
- **Día actual**
- **Últimos 3 días** (configurable)

**Ejemplo**:
- ✅ Noticia del 22 de diciembre → Válida
- ✅ Noticia del 20 de diciembre → Válida (dentro de 3 días)
- ❌ Noticia del 15 de diciembre → Rechazada (muy antigua)

### 2. Validación de Contenido Obsoleto

Se filtran noticias que mencionen información obsoleta:

**Palabras clave obsoletas**:
- "gerardo martino" / "tata martino" (ya no es DT)
- "sampaoli" (ya no es DT)
- "bauza" (ya no es DT)
- "maradona dt" (Maradona como DT, ya no aplica)
- "batista" (ya no es DT)
- "sabella" (ya no es DT)

**Excepciones**:
Si la noticia está en contexto histórico, se acepta:
- "histórico", "historia", "recordó", "pasado", etc.

**Ejemplo**:
- ❌ "Gerardo Martino sigue al frente de la selección" → Rechazada
- ✅ "Recordando cuando Gerardo Martino dirigía la selección" → Aceptada (contexto histórico)

## Cómo Funciona

### Integración Automática

La validación se aplica automáticamente en `fetch-news.py`:

```python
# Las noticias se validan antes de retornarse
validated_news = _validate_news_basic(unique_news, max_days=3)
```

### Script Independiente

También puedes validar noticias manualmente:

```bash
# Validar noticias desde archivo
python3 scripts/validate-news.py --input noticias.json --max-days 3

# Validar desde stdin
cat noticias.json | python3 scripts/validate-news.py --max-days 3
```

## Configuración

### Cambiar Días Máximos

Edita `scripts/fetch-news.py`:

```python
# Cambiar de 3 a 5 días
validated_news = _validate_news_basic(unique_news, max_days=5)
```

### Agregar Palabras Clave Obsoletas

Edita `scripts/fetch-news.py`, función `_validate_news_basic`:

```python
obsolete_keywords = [
    "gerardo martino", "tata martino", "sampaoli", "bauza",
    "maradona dt", "batista", "sabella",
    "nueva_palabra_aqui"  # Agregar aquí
]
```

## Ejemplos

### Noticia Válida

```json
{
  "title": "Scaloni confirmó la lista para el Mundial 2026",
  "description": "El entrenador anunció...",
  "published_at": "2025-12-22T10:00:00Z"
}
```
✅ **Válida**: Reciente y sin información obsoleta

### Noticia Rechazada (Fecha)

```json
{
  "title": "Argentina ganó el Mundial",
  "description": "...",
  "published_at": "2022-12-18T10:00:00Z"
}
```
❌ **Rechazada**: Muy antigua (más de 3 días)

### Noticia Rechazada (Contenido)

```json
{
  "title": "Gerardo Martino sigue al frente de la selección",
  "description": "El DT continúa...",
  "published_at": "2025-12-22T10:00:00Z"
}
```
❌ **Rechazada**: Contiene información obsoleta

### Noticia Aceptada (Contexto Histórico)

```json
{
  "title": "Recordando cuando Gerardo Martino dirigía la selección",
  "description": "En el pasado, el DT...",
  "published_at": "2025-12-22T10:00:00Z"
}
```
✅ **Aceptada**: Aunque menciona a Martino, está en contexto histórico

## Troubleshooting

### "No quedan noticias después de validar"

- Puede ser que todas las noticias sean muy antiguas
- O que todas contengan información obsoleta
- **Solución**: Ajustar `max_days` o revisar las palabras clave obsoletas

### "Noticias válidas pero incorrectas"

- La validación es básica, no puede detectar todos los casos
- **Solución**: Agregar más palabras clave obsoletas según necesidad

### "Noticias recientes pero obsoletas"

- La validación por contenido puede mejorarse
- **Solución**: Revisar manualmente y agregar más palabras clave

## Mejoras Futuras

- [ ] Validación más inteligente con LLM
- [ ] Lista de entrenadores actuales vs obsoletos
- [ ] Validación de jugadores (quién está activo)
- [ ] Cache de validaciones

---

*La validación garantiza que solo se usen noticias recientes y actualizadas*

