# InforMessi

Sistema automatizado de generación diaria de mensajes informativos previos al Mundial de Fútbol 2026.

## Descripción

InforMessi es un pipeline editorial automatizado con humano en el loop, inspirado en el proyecto manual Informesch (Mundial 2022). El objetivo es automatizar la producción diaria de contenido manteniendo una identidad editorial argentina, usando un LLM como redactor y herramientas de automatización low-code.

**Este proyecto NO es solo un bot**, sino un sistema completo que integra:
- Automatización de producción (n8n)
- Generación de contenido con LLM
- Revisión humana obligatoria
- Publicación controlada

## Identidad Editorial

El estilo emula Informesch, pero evolucionado:

- **Tono**: Argentino, cercano, editorial (no chat)
- **Estilo**: Informativo con humor sutil, no exagerado, no publicitario
- **Rigor**: No inventar datos, priorizar eventos reales
- **Límites**: No humor interno contextual viejo, no personas privadas, no política/violencia no deportiva
- **Cierre ritual**: "Coronados de gloria vivamos"

## Arquitectura General

```
┌─────────────────┐
│   Cron Trigger  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  n8n Workflow   │
│  - Recolecta    │
│    contexto     │
│  - Genera       │
│    mensaje      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preview        │
│  (Telegram)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Revisión       │
│  Humana         │
│  (Notion/       │
│   Telegram)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Publicación    │
│  (Telegram/X/   │
│   Instagram)    │
└─────────────────┘
```

### Componentes Principales

- **n8n**: Orquestación y automatización de workflows
- **LLM**: Redacción y edición de contenido (modelo local)
- **Telegram**: Preview y publicación
- **Notion/Telegram privado**: Revisión humana

## Estructura del Repositorio

```
InforMessi/
├── README.md                    # Este archivo
├── .gitignore                   # Archivos a ignorar
├── prompts/                     # Prompts para el LLM
│   ├── system-prompt.md         # Identidad editorial base
│   ├── main-editorial.md        # Prompt principal diario
│   ├── examples.md              # Ejemplos de mensajes
│   └── constraints.md           # Restricciones de contenido
├── data/                        # Datos estructurados
│   ├── events.json              # Eventos del día
│   └── templates.json           # Plantillas (opcional)
├── n8n/                         # Workflows de n8n
│   ├── workflows/               # Archivos exportados
│   └── README.md                # Documentación workflows
├── docs/                        # Documentación técnica
│   ├── architecture.md          # Arquitectura detallada
│   ├── editorial-guide.md      # Guía de estilo
│   └── deployment.md            # Guía de despliegue
├── scripts/                     # Scripts auxiliares
│   └── README.md
├── assets/                      # Recursos visuales y audiovisuales
│   ├── memes/                   # Memes de fútbol argentino
│   ├── media/                   # Material audiovisual
│   └── README.md                # Guía de assets
└── .env.example                 # Variables de entorno
```

## Estructura del Mensaje Diario

Cada mensaje sigue este esquema (flexible):

1. **Saludo** (ej: "Buenos días 🇦🇷")
2. **Cuenta regresiva** (ej: "Faltan X días para el Mundial 2026")
3. **Clima** (AMBA, La Plata y link a otras partes de Argentina)
4. **Bloque principal** (evento relevante del día)
5. **Bloque Argentina** (selección, jugador, historia)
6. **Dato del día** (mundial, país sede, cultura)
7. **Cierre** ("Buen día" + "Coronados de gloria vivamos")

**Longitud objetivo**: 90-130 palabras

## Plan de Trabajo

- **Fase 0**: Setup del repo + README ✅
- **Fase 1**: Diseño editorial + prompts ✅
- **Fase 2**: MVP con datos mock ✅
- **Fase 3**: Revisión humana
- **Fase 4**: APIs reales
- **Fase 5**: Visuales
- **Fase 6**: Publicación
- **Fase 7**: Documentación portfolio

## Próximos Pasos

1. Refinar prompts editoriales
2. Diseñar workflow n8n básico
3. Implementar generación con datos mock
4. Integrar revisión humana

## Créditos y Referencias

- Inspirado en **Informesch** (proyecto manual para Mundial 2022)
- Desarrollo para **Mundial de Fútbol 2026**

---

*Coronados de gloria vivamos*

