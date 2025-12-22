# Próximos Pasos - InforMessi

Guía de próximos pasos para completar y mejorar el sistema.

## ✅ Estado Actual

### Completado

- [x] **Fase 0**: Setup del repo + README
- [x] **Fase 1**: Diseño editorial + prompts
- [x] **Fase 2**: MVP con datos mock
- [x] **Fase 3**: Revisión humana (Telegram)
- [x] **Fase 4**: APIs reales (noticias, eventos)
- [x] Validación de noticias (fecha + contenido)
- [x] Secciones semanales automáticas
- [x] Scraper de Wikipedia para eventos históricos

### Pendiente

- [ ] **Fase 5**: Visuales (imágenes/gifs)
- [ ] **Fase 6**: Publicación en otras plataformas
- [ ] **Fase 7**: Documentación portfolio
- [ ] Automatización diaria (cron/n8n)
- [ ] Integración n8n (workflows)

---

## 🎯 Próximos Pasos Inmediatos

### 1. Scrapear Eventos de Wikipedia (Si no lo hiciste)

```bash
source venv/bin/activate

# Scrapear todos los meses (puede tardar 10-15 minutos)
python3 scripts/scrape-wikipedia-events.py --merge

# Verificar que se guardaron
python3 -c "import json; d=json.load(open('data/events.json')); print(f'Eventos: {len(d.get(\"events\", []))}')"
```

**Resultado esperado**: Cientos de eventos históricos agregados a `events.json`

---

### 2. Probar Flujo Completo Varias Veces

```bash
# Usar el script de flujo completo
bash scripts/daily-flow.sh

# O manualmente
source venv/bin/activate
export $(grep -v '^#' .env | grep -v '^$' | xargs)

python3 scripts/collect-daily-data.py --output /tmp/datos.json
python3 scripts/generate-message.py --data /tmp/datos.json --output /tmp/mensaje.txt
cat /tmp/mensaje.txt
```

**Objetivo**: Validar que los mensajes tienen buena calidad y variedad

---

### 3. Configurar Automatización Diaria

#### Opción A: Cron (Linux/Mac)

```bash
# Editar crontab
crontab -e

# Agregar (ejecuta a las 8:00 AM todos los días)
0 8 * * * cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi && bash scripts/daily-flow.sh >> /tmp/informessi-cron.log 2>&1
```

#### Opción B: n8n (Recomendado para portfolio)

1. Instalar n8n
2. Crear workflow que:
   - Ejecute `collect-daily-data.py`
   - Ejecute `generate-message.py`
   - Envíe a Telegram para revisión
   - Espere aprobación
   - Publique

---

### 4. Mejorar Calidad de Mensajes

**Ajustes posibles**:
- Refinar prompts según resultados
- Agregar más ejemplos a `prompts/examples.md`
- Ajustar longitud objetivo si es necesario
- Mejorar filtrado de noticias

---

### 5. Agregar Eventos Manuales

Edita `data/events.json` y agrega eventos importantes:

```json
{
  "events": [
    {
      "date": "2026-06-24",
      "type": "birthday",
      "priority": "high",
      "person": "Lionel Messi",
      "age": 39,
      "description": "Cumpleaños de Lionel Messi"
    },
    {
      "date": "2026-03-27",
      "type": "match",
      "priority": "critical",
      "description": "Argentina vs España - Finalissima",
      "opponent": "España",
      "venue": "Boston",
      "time": "20:00"
    }
  ]
}
```

---

## 🚀 Fase 5: Visuales (Próxima)

### Objetivos

- 1 imagen o gif por mensaje
- Relacionada con selección/jugador/mundial
- Rol secundario (contextual, no protagonista)

### Opciones

1. **Banco de imágenes curado**: Carpeta con imágenes pre-seleccionadas
2. **Generación con IA**: DALL-E, Midjourney, Stable Diffusion
3. **Reutilización inteligente**: Rotar imágenes según contexto

### Implementación Sugerida

```python
# scripts/get-image.py
def get_image_for_message(message_data):
    # Lógica para seleccionar/generar imagen
    # Basado en: día de semana, eventos, noticias
    pass
```

---

## 📱 Fase 6: Publicación Multiplataforma

### Plataformas Objetivo

1. **Telegram** ✅ (ya implementado)
2. **X (Twitter)** - Pendiente
3. **Instagram** - Pendiente

### Implementación

- Adaptar formato según plataforma
- Gestionar imágenes/videos
- Programar publicación

---

## 📚 Fase 7: Documentación Portfolio

### Documentos a Crear

1. **README.md completo** (ya existe, mejorar)
2. **Arquitectura técnica** (ya existe)
3. **Demo/GIF del flujo**
4. **Métricas/Resultados**
5. **Lecciones aprendidas**

---

## 🔧 Mejoras Técnicas Opcionales

### Corto Plazo

- [ ] Cache de eventos scrapeados (no re-scrapear cada vez)
- [ ] Mejor manejo de errores
- [ ] Logging estructurado
- [ ] Tests unitarios

### Mediano Plazo

- [ ] Notion para revisión (más robusto que Telegram)
- [ ] Dashboard de métricas
- [ ] A/B testing de prompts
- [ ] Análisis de engagement

---

## 📋 Checklist de Preparación para Producción

Antes de poner en producción diaria:

- [ ] Eventos de Wikipedia scrapeados
- [ ] Flujo completo probado 5+ veces
- [ ] Calidad de mensajes validada
- [ ] Automatización configurada (cron/n8n)
- [ ] Variables de entorno configuradas
- [ ] Backup de `events.json`
- [ ] Monitoreo básico (logs)

---

## 🎯 Recomendación Inmediata

**Haz esto ahora**:

1. ✅ Scrapear eventos de Wikipedia:
   ```bash
   python3 scripts/scrape-wikipedia-events.py --merge
   ```

2. ✅ Probar flujo completo 3-5 veces:
   ```bash
   bash scripts/daily-flow.sh
   ```

3. ✅ Revisar calidad de mensajes generados

4. ✅ Configurar automatización (cron o n8n)

5. ✅ Agregar eventos importantes manualmente a `events.json`

---

*El sistema está funcional. Solo falta automatizar y ajustar según resultados.*

