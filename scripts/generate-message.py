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

PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = PROJECT_ROOT / "data"

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

def load_prompt(filename):
    """Carga un archivo de prompt desde prompts/"""
    filepath = PROMPTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt no encontrado: {filename}")
    return filepath.read_text(encoding='utf-8')

# Función load_mock_data removida - ahora se carga directamente desde archivo JSON

def calculate_days_remaining(mundial_date, current_date):
    """Calcula días restantes hasta el Mundial"""
    mundial = datetime.strptime(mundial_date, "%Y-%m-%d").date()
    current = datetime.strptime(current_date, "%Y-%m-%d").date()
    return (mundial - current).days

def _format_event_for_selection(event):
    """Formatea un evento para el paso de seleccion."""
    if event.get("type") == "birthday":
        return f"{event.get('person', '')} cumple {event.get('age', '')} anos. {event.get('description', '')}".strip()
    if event.get("type") == "match":
        return (
            f"Partido: Argentina vs {event.get('opponent', '')} "
            f"en {event.get('venue', '')} a las {event.get('time', '')}. "
            f"{event.get('description', '')}"
        ).strip()
    return event.get("description", "")


def _format_event_for_prompt(event):
    """Formatea un evento para el prompt final."""
    if event.get("type") == "birthday":
        return f"- {event.get('person', '')} cumple {event.get('age', '')} años ({event.get('description', '')})"
    if event.get("type") == "match":
        return (
            f"- Partido: Argentina vs {event.get('opponent', '')} en {event.get('venue', '')} "
            f"a las {event.get('time', '')} ({event.get('description', '')})"
        )
    return f"- {event.get('description', '')}"


def _format_news_for_prompt(news):
    """Formatea una noticia para el prompt final."""
    title = news.get("title", "")
    desc = news.get("description", "")
    source = news.get("source", "Sin fuente")
    if desc:
        return f"- {title}: {desc[:150]} ({source})"
    return f"- {title} ({source})"


def build_selection_prompt(data):
    """Construye el prompt de seleccion de evidencias."""
    selector_prompt = load_prompt("selection-prompt.md")

    events = data.get("events", [])
    news = data.get("news", [])

    if events:
        events_lines = []
        for idx, event in enumerate(events, start=1):
            events_lines.append(f"- [E{idx}] {_format_event_for_selection(event)}")
        events_text = "\n".join(events_lines)
    else:
        events_text = "No hay eventos del dia."

    if news:
        news_lines = []
        for idx, item in enumerate(news, start=1):
            title = item.get("title", "")
            desc = item.get("description", "")
            source = item.get("source", "Sin fuente")
            news_lines.append(f"- [N{idx}] {title} | {desc[:140]} | {source}")
        news_text = "\n".join(news_lines)
    else:
        news_text = "No hay noticias del dia."

    prompt = f"""{selector_prompt}

### Eventos del Dia
{events_text}

### Noticias del Dia
{news_text}
"""
    return prompt


def _extract_json(text):
    """Extrae el primer objeto JSON de una respuesta."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start:end + 1]


def parse_selection_response(response_text, events, news):
    """Parsea la seleccion del LLM y devuelve items seleccionados."""
    selected_events = []
    selected_news = []

    raw_json = _extract_json(response_text)
    if not raw_json:
        return _fallback_selection(events, news)

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        return _fallback_selection(events, news)

    event_ids = data.get("selected_event_ids", []) or []
    news_ids = data.get("selected_news_ids", []) or []

    for event_id in event_ids:
        if isinstance(event_id, str) and event_id.startswith("E"):
            try:
                idx = int(event_id[1:]) - 1
                if 0 <= idx < len(events):
                    selected_events.append(events[idx])
            except ValueError:
                continue

    for news_id in news_ids:
        if isinstance(news_id, str) and news_id.startswith("N"):
            try:
                idx = int(news_id[1:]) - 1
                if 0 <= idx < len(news):
                    selected_news.append(news[idx])
            except ValueError:
                continue

    if not selected_events and not selected_news:
        return _fallback_selection(events, news)

    return selected_events, selected_news


def _fallback_selection(events, news):
    """Seleccion por defecto si falla el parseo."""
    selected_events = events[:1] if events else []
    selected_news = news[:2] if news else []
    return selected_events, selected_news


def build_prompt(data, selected_events=None, selected_news=None):
    """Construye el prompt completo con system prompt y datos del día"""
    
    # Cargar prompts
    system_prompt = load_prompt("system-prompt.md")
    main_prompt = load_prompt("main-editorial.md")
    
    # Agregar RAG de estilo desde informes editados
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from rag_style_learning import get_style_context
        style_context = get_style_context()
    except (ImportError, Exception) as e:
        style_context = ""  # Si no se puede importar, continuar sin RAG
    
    # Agregar RAG de memoria para evitar repeticiones (base de datos persistente)
    try:
        from rag_memory_database import build_memory_context_from_db
        memory_context = build_memory_context_from_db(data["date"])
    except (ImportError, Exception) as e:
        # Fallback al sistema anterior si no está disponible
        try:
            from rag_memory_system import build_memory_context
            memory_context = build_memory_context(data["date"], days_back=30)
        except:
            memory_context = ""
    
    # Agregar sección semanal según el día
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
    
    # Formatear eventos (seleccionados)
    events_to_use = selected_events if selected_events is not None else data.get("events", [])
    events_text = "No hay eventos importantes del día."
    if events_to_use:
        events_list = [_format_event_for_prompt(event) for event in events_to_use]
        events_text = "\n".join(events_list)

    # Formatear noticias (seleccionadas)
    news_to_use = selected_news if selected_news is not None else data.get("news", [])
    news_text = "No hay noticias relevantes del día."
    if news_to_use:
        news_list = [_format_news_for_prompt(item) for item in news_to_use]
        news_text = "\n".join(news_list)
    
    # Detectar contenido audiovisual
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from detect_media import get_media_for_date
        media = get_media_for_date(data["date"])
        media_context = ""
        if media and media.get("has_media"):
            media_context = f"\n### Contenido Visual Disponible\n"
            if media.get("images"):
                media_context += f"Hay {len(media['images'])} imagen(es) disponible(s) para este día.\n"
            if media.get("videos"):
                media_context += f"Hay {len(media['videos'])} video(s) disponible(s) para este día.\n"
            media_context += "Menciona el contenido visual en el mensaje si es relevante y apropiado.\n"
    except (ImportError, Exception):
        media_context = ""
    
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
{media_context}
{memory_context}
{style_context}
"""
    
    return prompt

def call_llm_ollama(prompt, model="qwen2.5:7b-instruct", base_url="http://localhost:11434", temperature=0.7, max_tokens=300):
    """Llama a Ollama para generar el mensaje"""
    import requests

    response = requests.post(
        f"{base_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        },
        timeout=120
    )
    response.raise_for_status()
    return response.json()["response"]


def call_llm_groq(prompt, model="llama-3.1-8b-instant", temperature=0.7, max_tokens=300):
    """Llama a Groq API (gratuita) para generar el mensaje"""
    import requests

    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        print("ERROR: GROQ_API_KEY no configurada")
        sys.exit(1)

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        },
        timeout=60
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _get_llm_caller(provider, model, base_url):
    """Returns a callable (prompt, temperature, max_tokens) -> str based on provider."""
    if provider == "groq":
        def _call(prompt, temperature=0.7, max_tokens=300):
            return call_llm_groq(prompt, model=model, temperature=temperature, max_tokens=max_tokens)
        return _call

    def _call(prompt, temperature=0.7, max_tokens=300):
        return call_llm_ollama(prompt, model=model, base_url=base_url, temperature=temperature, max_tokens=max_tokens)
    return _call

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Genera un mensaje de InforMessi usando LLM local"
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Archivo JSON con datos del día"
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("LLM_MODEL", "qwen2.5:7b-instruct"),
        help="Modelo a usar (default: env LLM_MODEL o qwen2.5:7b-instruct)"
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LLM_BASE_URL", "http://localhost:11434"),
        help="URL base de Ollama (default: env LLM_BASE_URL o http://localhost:11434)"
    )
    parser.add_argument(
        "--provider",
        default=os.environ.get("LLM_PROVIDER", "ollama"),
        choices=["ollama", "groq"],
        help="Proveedor LLM (default: env LLM_PROVIDER o ollama)"
    )
    parser.add_argument(
        "--output",
        help="Archivo donde guardar el mensaje generado"
    )
    
    args = parser.parse_args()
    
    print("🚀 InforMessi - Generador de Mensajes MVP")
    print("=" * 50)
    
    # Cargar datos
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ Archivo no encontrado: {data_path}")
        sys.exit(1)
    
    print(f"📂 Cargando datos: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   Fecha: {data['date']}")
    print(f"   Días restantes: {calculate_days_remaining(data['mundial_2026_start'], data['date'])}")
    print(f"   Eventos: {len(data.get('events', []))}")
    print(f"   Noticias: {len(data.get('news', []))}")
    
    llm_call = _get_llm_caller(args.provider, args.model, args.base_url)

    events = data.get("events", [])
    news = data.get("news", [])

    if events or news:
        print("\n🔎 Seleccionando eventos y noticias relevantes...")
        selection_prompt = build_selection_prompt(data)
        selection_response = llm_call(selection_prompt, temperature=0.1, max_tokens=200)
        selected_events, selected_news = parse_selection_response(
            selection_response, events, news
        )
        print(f"   Eventos seleccionados: {len(selected_events)}")
        print(f"   Noticias seleccionadas: {len(selected_news)}")
    else:
        print("\nℹ️  Sin eventos ni noticias, omitiendo paso de selección")
        selected_events, selected_news = [], []

    print("\n📝 Construyendo prompt...")
    prompt = build_prompt(data, selected_events, selected_news)

    print(f"\n🤖 Generando mensaje con {args.provider}/{args.model}...")
    print("   (Esto puede tardar unos momentos...)\n")

    message = llm_call(prompt)
    
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

