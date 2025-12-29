# Integración de APIs - InforMessi

Esta guía explica cómo configurar y usar las APIs reales en InforMessi (Fase 4).

## APIs Disponibles

### 1. Clima - OpenWeatherMap

#### Configuración

1. Regístrate en [OpenWeatherMap](https://openweathermap.org/api)
2. Obtén tu API key (gratis hasta 1000 llamadas/día)
3. Agrega a `.env`:

```env
WEATHER_API_KEY=tu_api_key_aqui
```

#### Uso

```bash
# Obtener clima
python3 scripts/fetch-weather.py

# Guardar en archivo
python3 scripts/fetch-weather.py --output /tmp/weather.json
```

#### Datos Obtenidos

- Temperatura min/max para AMBA (Buenos Aires)
- Temperatura min/max para La Plata
- Descripción del clima
- Link al pronóstico oficial argentino

### 2. Eventos - Archivo JSON

Los eventos se leen desde `data/events.json`.

#### Estructura

```json
{
  "events": [
    {
      "date": "2024-12-15",
      "type": "birthday",
      "priority": "high",
      "person": "Lionel Messi",
      "age": 37,
      "description": "Cumpleaños de Lionel Messi"
    }
  ]
}
```

#### Uso

```bash
# Obtener eventos del día
python3 scripts/fetch-events.py

# Obtener eventos de fecha específica
python3 scripts/fetch-events.py --date 2024-12-20
```

### 3. Noticias (Por Implementar)

Las noticias se pueden obtener de:

- **NewsAPI**: Noticias generales (requiere API key)
- **RSS Feeds**: Deportes argentinos
- **APIs especializadas**: Fútbol argentino

**Estado**: Pendiente de implementación

## Recolección Completa

### Script Integrado

```bash
# Recolectar todos los datos del día
python3 scripts/collect-daily-data.py --output /tmp/daily-data.json
```

Este script:
1. Obtiene clima real
2. Lee eventos del día
3. (Futuro) Obtiene noticias
4. Calcula días restantes
5. Guarda todo en un JSON

### Integración con Generación

```bash
# 1. Recolectar datos
python3 scripts/collect-daily-data.py --output /tmp/daily-data.json

# 2. Generar mensaje con datos reales
python3 scripts/generate-message.py --data /tmp/daily-data.json --output /tmp/mensaje.txt

# 3. Enviar para revisión
python3 scripts/telegram-preview.py \
  --message "$(cat /tmp/mensaje.txt)" \
  --preview-chat-id $TELEGRAM_PREVIEW_CHAT_ID \
  --token $TELEGRAM_BOT_TOKEN
```

## Alternativas de APIs

### Clima

- **OpenWeatherMap** (recomendado): Gratis hasta 1000 llamadas/día
- **WeatherAPI**: Alternativa gratuita
- **SMN Argentina**: API oficial (si está disponible)

### Noticias

- **NewsAPI**: Noticias generales
- **RSS Feeds**: TyC Sports, Olé, etc.
- **APIs de fútbol**: Si están disponibles

## Troubleshooting

### Error: "API key inválida"

- Verifica que la API key sea correcta
- Asegúrate de que esté en `.env` como `WEATHER_API_KEY`
- Verifica que la API key no haya expirado

### Error: "Rate limit exceeded"

- OpenWeatherMap tiene límite de 1000 llamadas/día (plan gratis)
- Considera cachear los datos
- Usa un plan pago si necesitas más

### Clima no disponible

- El script usará datos mock si la API falla
- Verifica tu conexión a internet
- Verifica que la API key sea válida

## Próximos Pasos

- [ ] Implementar fetch de noticias
- [ ] Agregar cache de datos
- [ ] Implementar fallback a datos mock
- [ ] Agregar más fuentes de datos

---

*Las APIs reales reemplazan los datos mock de la Fase 2*

