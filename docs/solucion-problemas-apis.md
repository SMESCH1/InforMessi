# Solución de Problemas con APIs

## Problema: Groq API - Error de autenticación

### Síntoma
```
❌ Error 401: API key inválida
```

### Causas Posibles

1. **API key incorrecta**
   - Verifica que empiece con `gsk_`
   - **Solución**: Genera una nueva key en https://console.groq.com/

2. **API key no configurada**
   - **Solución**: Agrega `GROQ_API_KEY=gsk_...` en `.env` o en GitHub Secrets

3. **Límite de rate alcanzado**
   - Groq tiene límites en el tier gratuito
   - **Solución**: Espera unos minutos y reintenta

---

## Problema: NewsAPI - Sin resultados

### Síntoma
```
⚠️ No se obtuvieron noticias de NewsAPI
```

### Causas Posibles

1. **API key no configurada**
   - **Solución**: Obtén una key en https://newsapi.org/ y agrega `NEWSAPI_KEY` en `.env`

2. **Límite diario alcanzado**
   - El tier gratuito permite 100 requests/día
   - **Solución**: Espera al día siguiente o usa RSS como fallback

### Soluciones alternativas

El sistema tiene múltiples fallbacks:
1. **NewsAPI** (principal)
2. **RSS feeds** (TyC Sports y otros)
3. **Scraping** (último recurso)

Sin noticias, el sistema genera mensajes usando solo eventos históricos.

---

## Problema: RSS Feeds no funcionan

### Síntoma
```
⚠️ Feed RSS inválido o no disponible
```

### Causa

Los sitios deportivos argentinos no siempre tienen RSS feeds públicos o las URLs cambian.

### Soluciones

1. **Configurar NewsAPI** (recomendado): obtén key en https://newsapi.org/
2. **Agregar eventos manuales**: edita `data/events.json` con eventos relevantes
3. El sistema funciona sin noticias — no es crítico para el flujo

### Verificar Noticias

```bash
source venv/bin/activate
python3 scripts/fetch-news.py
```

---

## Problema: Reddit API - Error de conexión

### Síntoma
```
❌ Error de autenticación con Reddit
```

### Causas Posibles

1. **Credenciales incorrectas**: Verifica `REDDIT_CLIENT_ID` y `REDDIT_CLIENT_SECRET`
2. **App de Reddit no es tipo "script"**: Recrea en https://www.reddit.com/prefs/apps
3. **User agent genérico**: Usa un user agent descriptivo como `InforMessi/1.0`

Reddit es opcional. Sin él, el sistema funciona con NewsAPI y RSS.

---

## Checklist de Solución

### LLM (Groq/Ollama)
- [ ] Groq: `GROQ_API_KEY` configurada en `.env` y GitHub Secrets
- [ ] Ollama: `ollama serve` corriendo y modelo descargado (`ollama pull qwen2.5:7b-instruct`)

### Noticias
- [ ] Configuré NewsAPI (opcional pero recomendado)
- [ ] Agregué eventos relevantes a `data/events.json`
- [ ] El sistema funciona sin noticias (no es crítico)

---

**El sistema funciona sin APIs externas configuradas**. Usa eventos históricos de `data/events.json` como base. Las APIs mejoran la calidad pero no son obligatorias para probar el flujo completo.
