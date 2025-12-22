# Clima Removido del Flujo - InforMessi

## Decisión

El clima ha sido removido del flujo principal de InforMessi y se deja como **feature futura opcional**.

## Cambios Realizados

### Prompts Actualizados

- ✅ `prompts/main-editorial.md`: Removido bloque de clima (ahora 6 bloques en lugar de 7)
- ✅ `prompts/examples.md`: Todos los ejemplos actualizados sin clima
- ✅ `prompts/system-prompt.md`: Estructura actualizada

### Scripts Actualizados

- ✅ `scripts/collect-daily-data.py`: No recolecta clima
- ✅ `scripts/generate-message.py`: No incluye clima en el prompt
- ✅ `scripts/fetch-weather.py`: Mantenido para uso futuro (no se usa en flujo principal)

### Estructura del Mensaje

**Antes (7 bloques)**:
1. Saludo
2. Cuenta regresiva
3. **Clima** ❌ (removido)
4. Bloque principal
5. Bloque Argentina
6. Dato del día
7. Cierre

**Ahora (6 bloques)**:
1. Saludo
2. Cuenta regresiva
3. Bloque principal
4. Bloque Argentina
5. Dato del día
6. Cierre

## Feature Futura

Si en el futuro se quiere agregar clima:

1. El script `scripts/fetch-weather.py` ya existe
2. Solo hay que:
   - Agregar clima de vuelta a `collect-daily-data.py`
   - Actualizar los prompts
   - Configurar API key de OpenWeatherMap

## Estado Actual

- ✅ Mensajes se generan sin clima
- ✅ Estructura de 6 bloques funcionando
- ✅ Longitud objetivo mantenida (90-130 palabras)
- ✅ Todos los ejemplos actualizados

---

*El clima puede agregarse en el futuro si se considera necesario, pero no es crítico para el funcionamiento del sistema.*

