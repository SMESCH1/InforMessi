# Scripts Auxiliares - InforMessi

Este directorio contiene scripts auxiliares que pueden ser necesarios para el funcionamiento del sistema.

## Scripts Disponibles

### `generate-message.py`

Script de prueba para generar mensajes con LLM local (Ollama).

#### Requisitos

```bash
pip install requests
```

#### Uso Básico

```bash
python scripts/generate-message.py
```

#### Opciones

```bash
python scripts/generate-message.py \
  --data mock-data.json \
  --model llama3.2 \
  --base-url http://localhost:11434 \
  --output mensaje-generado.txt
```

#### Parámetros

- `--data`: Archivo de datos mock a usar (default: `mock-data.json`)
- `--model`: Modelo de Ollama a usar (default: `llama3.2`)
- `--base-url`: URL base de Ollama (default: `http://localhost:11434`)
- `--output`: Archivo donde guardar el mensaje generado (opcional)

#### Ejemplos

```bash
# Usar datos mock con evento importante
python scripts/generate-message.py --data mock-data.json

# Usar datos mock sin evento
python scripts/generate-message.py --data mock-data-no-event.json

# Usar datos mock con partido
python scripts/generate-message.py --data mock-data-match.json

# Guardar resultado en archivo
python scripts/generate-message.py --output mensaje.txt
```

#### Datos Mock Disponibles

- `mock-data.json`: Día con cumpleaños de Messi
- `mock-data-no-event.json`: Día sin evento importante
- `mock-data-match.json`: Día con partido de la selección

## Propósito

Los scripts aquí pueden servir para:

- Procesamiento de datos
- Utilidades de formato
- Validación de contenido
- Testing y debugging
- Tareas de mantenimiento

## Estructura

```
scripts/
├── README.md          # Este archivo
├── generate-message.py # Generador de mensajes (MVP)
└── [otros scripts según necesidad]
```

## Nota sobre Tecnología

El proyecto es flexible en cuanto a tecnología. Los scripts pueden estar en:
- Python
- Node.js
- Bash
- O cualquier lenguaje que sea necesario

## Cuándo Usar Scripts

Usa scripts cuando:
- n8n no puede hacer algo directamente
- Necesitas procesamiento complejo de datos
- Requieres validaciones específicas
- Necesitas herramientas de línea de comandos
- Quieres probar componentes antes de integrarlos

## Cuándo NO Usar Scripts

Evita scripts cuando:
- n8n puede hacerlo directamente
- Agrega complejidad innecesaria
- Puede resolverse con configuración

## Próximos Pasos

Los scripts se crearán según necesidad durante el desarrollo.

---

*Mantener este directorio simple y solo agregar scripts cuando sean realmente necesarios*
