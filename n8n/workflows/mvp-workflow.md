# Workflow MVP - InforMessi

Documentación del workflow básico para la Fase 2 (MVP con datos mock).

## Estructura del Workflow

```
┌─────────────────┐
│  Manual Trigger │  (Para testing)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Load Mock Data │  (Read Binary File)
│  data/mock-data │
│  .json          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Build Prompt   │  (Code/Function)
│  - System       │
│  - Main         │
│  - Data         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Call LLM       │  (HTTP Request)
│  Ollama API     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Format Output  │  (Code/Function)
│  Clean message  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Display Result │  (Output/Log)
└─────────────────┘
```

## Nodos del Workflow

### 1. Manual Trigger
- **Tipo**: Manual Trigger
- **Propósito**: Iniciar el workflow manualmente para testing
- **Configuración**: Sin configuración especial

### 2. Load Mock Data
- **Tipo**: Read Binary File
- **Propósito**: Cargar datos mock desde `data/mock-data.json`
- **Configuración**:
  - File Path: `{{ $env.PROJECT_ROOT }}/data/mock-data.json`
  - Encoding: UTF-8
- **Output**: JSON con datos del día

### 3. Build Prompt
- **Tipo**: Code / Function
- **Propósito**: Construir el prompt completo combinando system prompt, main prompt y datos
- **Lógica**:
  1. Leer `prompts/system-prompt.md`
  2. Leer `prompts/main-editorial.md`
  3. Formatear datos del día
  4. Combinar todo en un prompt final
- **Input**: Datos mock del nodo anterior
- **Output**: Prompt completo como string

### 4. Call LLM (Ollama)
- **Tipo**: HTTP Request
- **Propósito**: Llamar a la API de Ollama para generar el mensaje
- **Configuración**:
  - Method: POST
  - URL: `{{ $env.LLM_BASE_URL }}/api/generate`
  - Headers: `Content-Type: application/json`
  - Body (JSON):
    ```json
    {
      "model": "{{ $env.LLM_MODEL }}",
      "prompt": "{{ $json.prompt }}",
      "stream": false,
      "options": {
        "temperature": 0.7,
        "max_tokens": 300
      }
    }
    ```
- **Output**: Respuesta de Ollama con mensaje generado

### 5. Format Output
- **Tipo**: Code / Function
- **Propósito**: Limpiar y formatear el mensaje generado
- **Lógica**:
  - Extraer el texto del mensaje de la respuesta
  - Limpiar markdown si existe
  - Validar longitud (90-130 palabras)
- **Output**: Mensaje formateado listo para usar

### 6. Display Result
- **Tipo**: Output / Log
- **Propósito**: Mostrar el resultado final
- **Configuración**: Mostrar mensaje generado

## Variables de Entorno Necesarias

```env
PROJECT_ROOT=/ruta/al/proyecto/InforMessi
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
```

## Flujo de Datos

1. **Trigger** → Inicia el workflow
2. **Load Mock Data** → Carga `data/mock-data.json`
3. **Build Prompt** → Construye prompt con:
   - System prompt (identidad editorial)
   - Main prompt (estructura del día)
   - Datos del día (clima, eventos, noticias)
4. **Call LLM** → Genera mensaje con Ollama
5. **Format Output** → Limpia y formatea
6. **Display Result** → Muestra resultado

## Próximos Pasos (Fase 3+)

- Agregar nodo de Telegram para preview
- Agregar lógica de revisión humana
- Agregar nodo de publicación
- Cambiar trigger manual por cron diario
- Integrar APIs reales (clima, noticias)

## Notas de Implementación

- Este workflow es para **testing y desarrollo**
- Los datos son **mock** (no APIs reales)
- El trigger es **manual** (no automático)
- No incluye **revisión humana** todavía
- No incluye **publicación** todavía

---

*Workflow para Fase 2 (MVP). Se expandirá en fases siguientes.*

