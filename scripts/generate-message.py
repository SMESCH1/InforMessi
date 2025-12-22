#!/usr/bin/env python3
"""
Script de prueba para generar mensajes con LLM local
MVP - Fase 2 - InforMessi
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, date

# Configuración
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = PROJECT_ROOT / "data"

def load_prompt(filename):
    """Carga un archivo de prompt desde prompts/"""
    filepath = PROMPTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt no encontrado: {filename}")
    return filepath.read_text(encoding='utf-8')

def load_mock_data(filename="mock-data.json"):
    """Carga datos mock desde data/"""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Datos mock no encontrados: {filename}")
    return json.loads(filepath.read_text(encoding='utf-8'))

def calculate_days_remaining(mundial_date, current_date):
    """Calcula días restantes hasta el Mundial"""
    mundial = datetime.strptime(mundial_date, "%Y-%m-%d").date()
    current = datetime.strptime(current_date, "%Y-%m-%d").date()
    return (mundial - current).days

def build_prompt(data):
    """Construye el prompt completo con system prompt y datos del día"""
    
    # Cargar prompts
    system_prompt = load_prompt("system-prompt.md")
    main_prompt = load_prompt("main-editorial.md")
    
    # Agregar sección semanal según el día
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from generate_weekly_sections import build_weekly_section_prompt
        weekly_section = build_weekly_section_prompt(data["date"])
    except ImportError:
        weekly_section = ""  # Si no se puede importar, continuar sin sección especial
    
    # Calcular días restantes
    days_remaining = calculate_days_remaining(
        data["mundial_2026_start"],
        data["date"]
    )
    
    # Formatear eventos
    events_text = "No hay eventos importantes del día."
    if data["events"]:
        events_list = []
        for event in data["events"]:
            if event["type"] == "birthday":
                events_list.append(
                    f"- {event['person']} cumple {event['age']} años ({event['description']})"
                )
            elif event["type"] == "match":
                events_list.append(
                    f"- Partido: Argentina vs {event['opponent']} en {event['venue']} a las {event['time']} ({event['description']})"
                )
            else:
                events_list.append(f"- {event['description']}")
        events_text = "\n".join(events_list)
    
    # Formatear noticias
    news_text = "No hay noticias relevantes del día."
    if data.get("news"):
        news_list = []
        for news in data["news"]:
            # Usar 'description' si existe, sino 'title' solo
            desc = news.get("description", news.get("title", ""))
            news_list.append(f"- {news['title']}: {desc[:150]}")
        news_text = "\n".join(news_list)
    
    # Construir prompt con datos
    prompt = f"""{system_prompt}

---

{main_prompt}

### Datos del Día
- **Fecha**: {data['date']}
- **Días restantes al Mundial 2026**: {days_remaining} días

### Eventos del Día
{events_text}

### Noticias Relevantes
{news_text}
{weekly_section}
"""
    
    return prompt

def call_llm_ollama(prompt, model="llama3.2", base_url="http://localhost:11434"):
    """Llama a Ollama para generar el mensaje"""
    try:
        import requests
        
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 300
                }
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["response"]
    except ImportError:
        print("ERROR: Necesitas instalar 'requests': pip install requests")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"ERROR: No se pudo conectar a Ollama en {base_url}")
        print("Asegúrate de que Ollama esté corriendo y el modelo {model} esté instalado")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR al llamar a Ollama: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Genera un mensaje de InforMessi usando LLM local"
    )
    parser.add_argument(
        "--data",
        default="mock-data.json",
        help="Archivo de datos mock a usar (default: mock-data.json)"
    )
    parser.add_argument(
        "--model",
        default="llama3.2",
        help="Modelo de Ollama a usar (default: llama3.2)"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:11434",
        help="URL base de Ollama (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--output",
        help="Archivo donde guardar el mensaje generado"
    )
    
    args = parser.parse_args()
    
    print("🚀 InforMessi - Generador de Mensajes MVP")
    print("=" * 50)
    
    # Cargar datos
    print(f"📂 Cargando datos mock: {args.data}")
    data = load_mock_data(args.data)
    print(f"   Fecha: {data['date']}")
    print(f"   Días restantes: {calculate_days_remaining(data['mundial_2026_start'], data['date'])}")
    print(f"   Eventos: {len(data['events'])}")
    print(f"   Noticias: {len(data['news'])}")
    
    # Construir prompt
    print("\n📝 Construyendo prompt...")
    prompt = build_prompt(data)
    
    # Generar mensaje
    print(f"\n🤖 Generando mensaje con {args.model}...")
    print("   (Esto puede tardar unos momentos...)\n")
    
    message = call_llm_ollama(prompt, args.model, args.base_url)
    
    # Mostrar resultado
    print("=" * 50)
    print("📨 MENSAJE GENERADO:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    # Guardar si se especificó output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(message, encoding='utf-8')
        print(f"\n💾 Mensaje guardado en: {output_path}")
    
    # Estadísticas
    word_count = len(message.split())
    print(f"\n📊 Estadísticas:")
    print(f"   Palabras: {word_count}")
    print(f"   Longitud objetivo: 90-130 palabras")
    if 90 <= word_count <= 130:
        print("   ✅ Longitud apropiada")
    else:
        print("   ⚠️  Longitud fuera del rango objetivo")

if __name__ == "__main__":
    main()

