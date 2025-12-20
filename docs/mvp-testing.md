# Guía de Testing del MVP - InforMessi

Esta guía explica cómo probar el MVP (Fase 2) del sistema InforMessi.

## Objetivo del MVP

El MVP permite:
- Generar mensajes usando LLM local (Ollama)
- Probar con datos mock (sin APIs reales)
- Validar la calidad de los prompts
- Ajustar parámetros antes de integrar con n8n

## Requisitos Previos

### 1. Ollama Instalado y Corriendo

```bash
# Verificar que Ollama esté instalado
ollama --version

# Verificar que esté corriendo
curl http://localhost:11434/api/tags

# Instalar modelo (si no lo tienes)
ollama pull llama3.2
```

### 2. Python y Dependencias

```bash
# Python 3.8+
python3 --version

# Instalar dependencias
pip install requests
```

### 3. Datos Mock

Los datos mock están en `data/`:
- `mock-data.json` - Día con evento importante
- `mock-data-no-event.json` - Día sin evento
- `mock-data-match.json` - Día con partido

## Testing con Script Python

### Uso Básico

```bash
# Desde la raíz del proyecto
python3 scripts/generate-message.py
```

### Con Diferentes Datos Mock

```bash
# Día con cumpleaños de Messi
python3 scripts/generate-message.py --data mock-data.json

# Día sin evento importante
python3 scripts/generate-message.py --data mock-data-no-event.json

# Día con partido
python3 scripts/generate-message.py --data mock-data-match.json
```

### Con Diferentes Modelos

```bash
# Usar otro modelo de Ollama
python3 scripts/generate-message.py --model llama3.1

# Especificar URL de Ollama
python3 scripts/generate-message.py --base-url http://localhost:11434
```

### Guardar Resultado

```bash
# Guardar mensaje generado en archivo
python3 scripts/generate-message.py --output mensaje-generado.txt
```

## Checklist de Validación

Al probar el MVP, verificar:

### Estructura del Mensaje

- [ ] Incluye saludo
- [ ] Incluye cuenta regresiva
- [ ] Incluye clima (AMBA, La Plata, link)
- [ ] Incluye bloque principal
- [ ] Incluye bloque Argentina
- [ ] Incluye dato del día
- [ ] Incluye cierre con frase ritual

### Calidad del Contenido

- [ ] Tono argentino y cercano
- [ ] No es publicitario
- [ ] No inventa datos
- [ ] Prioriza eventos importantes (si los hay)
- [ ] Longitud entre 90-130 palabras
- [ ] Frase ritual presente: "Coronados de gloria vivamos"

### Casos de Prueba

#### Caso 1: Día con Evento Importante
- **Archivo**: `mock-data.json`
- **Verificar**: El mensaje debe centrarse en el cumpleaños de Messi
- **Esperado**: Bloque principal habla del evento

#### Caso 2: Día Sin Evento
- **Archivo**: `mock-data-no-event.json`
- **Verificar**: El mensaje usa formato estándar
- **Esperado**: Bloque principal con noticia o dato interesante

#### Caso 3: Día con Partido
- **Archivo**: `mock-data-match.json`
- **Verificar**: El mensaje prioriza el partido
- **Esperado**: Bloque principal habla del partido

## Ajustes y Mejoras

### Si el Mensaje es Muy Corto o Largo

Ajustar en el prompt o en los parámetros del LLM:
- `temperature`: Aumentar para más creatividad (0.7-0.9)
- `max_tokens`: Aumentar para mensajes más largos (300-500)

### Si el Tono No es Correcto

Revisar y ajustar:
- `prompts/system-prompt.md` - Identidad editorial
- `prompts/examples.md` - Agregar más ejemplos

### Si Faltan Elementos

Verificar:
- `prompts/main-editorial.md` - Estructura requerida
- Datos mock - Que incluyan toda la información necesaria

## Próximos Pasos

Una vez validado el MVP:

1. **Integrar con n8n**: Crear workflow real en n8n
2. **Agregar revisión humana**: Sistema de preview en Telegram
3. **Integrar APIs reales**: Clima, noticias (Fase 4)
4. **Automatizar**: Trigger diario con cron

## Troubleshooting

### Error: "No se pudo conectar a Ollama"

- Verificar que Ollama esté corriendo: `ollama serve`
- Verificar URL: `curl http://localhost:11434/api/tags`

### Error: "Modelo no encontrado"

- Instalar modelo: `ollama pull llama3.2`
- Verificar modelos disponibles: `ollama list`

### Error: "Prompt no encontrado"

- Verificar que estés en la raíz del proyecto
- Verificar que existan los archivos en `prompts/`

### Mensaje Generado es Muy Corto

- Aumentar `max_tokens` en la llamada a Ollama
- Revisar que el prompt incluya suficiente contexto

### Mensaje Generado es Muy Largo

- Reducir `max_tokens`
- Ajustar instrucciones de longitud en el prompt

---

*Esta guía se actualizará según avance el proyecto*

