# Solución de Problemas con APIs

## 🌤 Problema: API de Clima - Error 401

### Síntoma
```
❌ Error 401: API key inválida o no activada
```

### Causas Posibles

1. **API key recién creada** (más común)
   - OpenWeatherMap requiere 10-15 minutos para activar la key
   - **Solución**: Espera 10-15 minutos y prueba de nuevo

2. **API key copiada incorrectamente**
   - Puede tener espacios al inicio/final
   - **Solución**: Verifica que no haya espacios en `.env`

3. **API key inválida**
   - La key fue revocada o eliminada
   - **Solución**: Genera una nueva key en https://home.openweathermap.org/api_keys

### Verificar API Key

```bash
source venv/bin/activate
python3 scripts/test-weather-api.py
```

### Solución Rápida

1. Ve a: https://home.openweathermap.org/api_keys
2. Verifica que tu key esté activa (debe aparecer en la lista)
3. Si acabas de crearla, espera 10-15 minutos
4. Prueba de nuevo: `python3 scripts/test-weather-api.py`

### Mientras tanto

El sistema funciona con datos por defecto. No es crítico para probar el flujo.

---

## 📰 Problema: RSS Feeds no funcionan

### Síntoma
```
⚠️  Feed RSS inválido o no disponible
⚠️  No se obtuvieron noticias
```

### Causa

Los sitios deportivos argentinos no siempre tienen RSS feeds públicos o las URLs cambian.

### Soluciones

#### Opción 1: Usar NewsAPI (Recomendado)

1. Obtén API key en: https://newsapi.org/
2. Agrega a `.env`:
   ```env
   NEWSAPI_KEY=tu_api_key
   ```
3. El script usará NewsAPI automáticamente

#### Opción 2: Mejorar Scraping

El scraping de TyC Sports puede mejorarse. Por ahora, el sistema funciona sin noticias.

#### Opción 3: Agregar Eventos Manuales

En lugar de noticias automáticas, agrega eventos relevantes a `data/events.json`.

### Verificar Noticias

```bash
source venv/bin/activate
python3 scripts/fetch-news.py
```

---

## ✅ Checklist de Solución

### Clima
- [ ] Esperé 10-15 minutos después de crear la API key
- [ ] Verifiqué la key en https://home.openweathermap.org/api_keys
- [ ] Probé con `python3 scripts/test-weather-api.py`
- [ ] La key no tiene espacios en `.env`

### Noticias
- [ ] Configuré NewsAPI (opcional pero recomendado)
- [ ] Agregué eventos relevantes a `data/events.json`
- [ ] El sistema funciona sin noticias (no es crítico)

---

## 💡 Nota Importante

**El sistema funciona sin APIs configuradas**. Usa datos por defecto y funciona correctamente. Las APIs mejoran la calidad pero no son obligatorias para probar el flujo completo.

