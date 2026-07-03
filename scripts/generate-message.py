#!/usr/bin/env python3
"""
Script de prueba para generar mensajes con LLM local
MVP - Fase 2 - InforMessi
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, date

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

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

def format_countdown(days_remaining, mundial_phase=None, mundial_day=None):
    """Formatea la cuenta regresiva según la fase del Mundial."""
    if mundial_phase == "durante_mundial" and mundial_day is not None:
        return f"Día {mundial_day} del Mundial 2026"
    elif days_remaining == 0:
        return "Hoy comienza el Mundial 2026"
    elif days_remaining == 1:
        return "Falta 1 día para el Mundial 2026"
    elif days_remaining > 1:
        return f"Faltan {days_remaining} días para el Mundial 2026"
    else:
        return f"Día {abs(days_remaining) + 1} del Mundial 2026"

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


def _format_event_for_prompt(event, report_date=None):
    """Formatea un evento para el prompt final, incluyendo año y antigüedad."""
    ev_date = event.get("date", "")
    ev_year = None
    years_ago = None
    if isinstance(ev_date, str) and len(ev_date) >= 4:
        try:
            ev_year = int(ev_date[:4])
            if report_date and ev_year < int(report_date[:4]):
                years_ago = int(report_date[:4]) - ev_year
        except ValueError:
            pass

    if event.get("type") == "birthday":
        return f"- {event.get('person', '')} cumple {event.get('age', '')} años ({event.get('description', '')})"
    if event.get("type") == "match":
        return (
            f"- Partido: Argentina vs {event.get('opponent', '')} en {event.get('venue', '')} "
            f"a las {event.get('time', '')} ({event.get('description', '')})"
        )
    # Para efemérides históricas: incluir año original y años transcurridos
    desc = event.get("description", "")
    if years_ago is not None and ev_year is not None:
        return f"- [Año: {ev_year}, hace {years_ago} años] {desc}"
    elif ev_year is not None:
        return f"- [Año: {ev_year}] {desc}"
    return f"- {desc}"


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
        events_list = [_format_event_for_prompt(event, report_date=data["date"]) for event in events_to_use]
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
    countdown_text = format_countdown(
        days_remaining,
        data.get("mundial_phase"),
        data.get("mundial_day")
    )

    prompt = f"""{system_prompt}

---

{main_prompt}

### Datos del Día
- **Fecha**: {data['date']}
- **Cuenta regresiva**: {countdown_text}

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


def call_llm_groq(prompt, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=500):
    """Llama a Groq API (gratuita) para generar el mensaje, con retry en rate limit.

    Wrapper delgado sobre llm_client.call_groq (mantenido por compatibilidad).
    Puede propagar LLMClientError (p.ej. si falta GROQ_API_KEY); main() la
    captura para preservar el comportamiento CLI (exit 1 con mensaje claro).
    """
    sys.path.insert(0, str(Path(__file__).parent))
    from llm_client import call_groq
    return call_groq(prompt, model=model, temperature=temperature, max_tokens=max_tokens)


def _get_llm_caller(provider, model, base_url):
    """Returns a callable (prompt, temperature, max_tokens) -> str based on provider."""
    if provider == "groq":
        def _call(prompt, temperature=0.7, max_tokens=500):
            return call_llm_groq(prompt, model=model, temperature=temperature, max_tokens=max_tokens)
        return _call

    def _call(prompt, temperature=0.7, max_tokens=500):
        return call_llm_ollama(prompt, model=model, base_url=base_url, temperature=temperature, max_tokens=max_tokens)
    return _call

CIERRE_RITUAL = "Coronados de gloria vivamos"
CIERRE_COMPLETO = "Coronados de gloria vivamos 🩵🤍🩵"

# Patrones de meta-texto que el LLM a veces agrega
_META_PATTERNS = [
    re.compile(r"^(Aquí\s+(está|te\s+dejo|va)\s+.*?:?\s*)$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^(Here\s+is.*?:?\s*)$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\*\*Sección.*?\*\*\s*$", re.MULTILINE),
    re.compile(r"^#+\s+.*$", re.MULTILINE),  # headers markdown
]


def _build_safe_message(days_remaining, mundial_phase=None, mundial_day=None, weather=None):
    """Genera un mensaje mínimo seguro: saludo + cuenta regresiva + (clima) + cierre doble."""
    countdown = format_countdown(days_remaining, mundial_phase, mundial_day)
    blocks = [f"Buenos días 🇦🇷", f"{countdown} ⚽"]
    if weather:
        blocks.append(_format_weather_block(weather))
    blocks.append(f"Buen día\n{CIERRE_COMPLETO}")
    return "\n\n".join(blocks)


def _format_weather_block(weather):
    """Formatea el bloque de clima determinístico (import perezoso de fetch-weather.py,
    que tiene guion en el nombre)."""
    from importlib import import_module
    sys.path.insert(0, str(Path(__file__).parent))
    _fw = import_module("fetch-weather")
    return _fw.format_weather_block(weather)


# Líneas que el LLM a veces escribe mencionando clima/temperaturas, pese a
# la instrucción explícita de no hacerlo (defensa: el bloque es 100%
# determinístico e inyectado por postprocess_message).
#
# El filtro está acotado a patrones que efectivamente hablan del clima
# meteorológico, para no eliminar de más frases como "el clima tenso del
# vestuario" o "ganó por 30 grados de diferencia en el ranking" (falsos
# positivos confirmados empíricamente). Una línea se elimina SOLO si:
#   (a) tiene un patrón numérico de temperatura (-12° / 30 grados) JUNTO a
#       contexto meteorológico (mín/máx/térmica/temperatura/pronóstico) en
#       la misma línea, o
#   (b) "clima" aparece cerca de AMBA/La Plata/pronóstico/temperatura/
#       soleado/lluvia/nublado, o
#   (c) la línea empieza con uno de los emojis del bloque de clima.
_WEATHER_TEMP_CONTEXT_RE = re.compile(
    r"m[ií]n(?:\.|ima)?|m[aá]x(?:\.|ima)?|t[eé]rmica|temperatura|pron[oó]stico",
    re.IGNORECASE,
)
_WEATHER_TEMP_NUMBER_RE = re.compile(r"-?\d+\s*°|\d+\s*grados?\b", re.IGNORECASE)
_WEATHER_CLIMA_WORD_RE = re.compile(r"clima", re.IGNORECASE)
_WEATHER_CLIMA_CONTEXT_RE = re.compile(
    r"amba|la\s+plata|pron[oó]stico|temperatura|soleado|lluvia|nublado",
    re.IGNORECASE,
)
_WEATHER_EMOJI_START_RE = re.compile(r"^\s*[\U0001F324\U0001F326\U0001F327☀️]")


def _is_llm_weather_line(line):
    """True si la línea debe descartarse por hablar del clima meteorológico."""
    if _WEATHER_EMOJI_START_RE.match(line):
        return True
    if _WEATHER_TEMP_NUMBER_RE.search(line) and _WEATHER_TEMP_CONTEXT_RE.search(line):
        return True
    if _WEATHER_CLIMA_WORD_RE.search(line) and _WEATHER_CLIMA_CONTEXT_RE.search(line):
        return True
    return False


def _strip_llm_weather_mentions(message):
    """Elimina líneas escritas por el LLM que mencionan clima/temperaturas."""
    lines = message.split("\n")
    kept = []
    for ln in lines:
        if _is_llm_weather_line(ln):
            logger.info(f"Descartando línea por mención de clima del LLM: {ln!r}")
            continue
        kept.append(ln)
    cleaned = "\n".join(kept)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _inject_weather_block(message, weather):
    """Inserta el bloque de clima determinístico inmediatamente después de la
    línea de cuenta regresiva (si se encuentra) o después de la primera línea
    (saludo) en caso contrario."""
    weather_block = _format_weather_block(weather)
    lines = message.split("\n")

    countdown_idx = None
    for i, ln in enumerate(lines):
        stripped = ln.strip()
        if re.match(r"^(Faltan?\s+\d+\s+d[ií]as?\s+para\s+el\s+Mundial\s+2026|"
                     r"Hoy\s+comienza\s+el\s+Mundial\s+2026|"
                     r"D[ií]a\s+\d+\s+del\s+Mundial\s+2026)", stripped, re.IGNORECASE):
            countdown_idx = i
            break

    if countdown_idx is not None:
        insert_at = countdown_idx + 1
    else:
        # Insertar después de la primera línea no vacía (saludo)
        insert_at = 0
        for i, ln in enumerate(lines):
            if ln.strip():
                insert_at = i + 1
                break

    new_lines = lines[:insert_at] + ["", weather_block, ""] + lines[insert_at:]
    result = "\n".join(new_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def _ensure_cierre_doble(message):
    """Asegura que el mensaje termine con la línea 'Buen día' inmediatamente
    antes del cierre ritual 'Coronados de gloria vivamos 🩵🤍🩵', preservando
    el resto de la estructura de líneas/párrafos del mensaje sin reformatear."""
    all_lines = message.split("\n")
    non_empty_idx = [i for i, ln in enumerate(all_lines) if ln.strip()]
    if not non_empty_idx:
        return message

    last_idx = non_empty_idx[-1]
    ultima = all_lines[last_idx]
    if CIERRE_RITUAL.lower() not in ultima.lower():
        return message  # el cierre ritual se asegura en otro paso

    if len(non_empty_idx) >= 2:
        prev_idx = non_empty_idx[-2]
        if all_lines[prev_idx].strip() == "Buen día":
            return message  # ya tiene cierre doble

    new_lines = all_lines[:last_idx] + ["Buen día"] + all_lines[last_idx:]
    return "\n".join(new_lines)


def _extract_allowed_entities(events, news):
    """Extrae nombres, años y scores permitidos desde los datos de entrada."""
    allowed_years = set()
    allowed_persons = set()
    allowed_scores = set()

    for ev in events:
        # Años desde la fecha del evento
        ev_date = ev.get("date", "")
        if isinstance(ev_date, str) and len(ev_date) >= 4:
            try:
                allowed_years.add(int(ev_date[:4]))
            except ValueError:
                pass

        # Persona
        person = ev.get("person", "")
        if person:
            allowed_persons.add(person.lower())
            # Agregar apellido solo también
            parts = person.strip().split()
            if len(parts) > 1:
                allowed_persons.add(parts[-1].lower())

        # Scores del tipo "4-0", "6-1" en la descripción
        desc = ev.get("description", "")
        for m in re.findall(r"\b(\d+-\d+)\b", desc):
            allowed_scores.add(m)

    for nw in news:
        title = nw.get("title", "")
        desc = nw.get("description", "")
        for text in (title, desc):
            for m in re.findall(r"\b((?:19|20)\d{2})\b", text):
                allowed_years.add(int(m))
            for m in re.findall(r"\b(\d+-\d+)\b", text):
                allowed_scores.add(m)

    # Siempre permitir años de contexto general
    allowed_years.update({2026, 2025, 1978, 1986, 2022})

    return allowed_years, allowed_persons, allowed_scores


def postprocess_message(message, data, days_remaining):
    """Post-procesa el mensaje para validar y limpiar alucinaciones.

    Reglas:
    1. Si no había eventos ni noticias, forzar mensaje básico.
    2. Limpiar markdown y meta-texto.
    3. Verificar años mencionados contra datos de entrada.
    4. Verificar scores mencionados contra datos de entrada.
    5. Asegurar cierre ritual.
    """
    events = data.get("events", [])
    news = data.get("news", [])
    weather = data.get("weather")

    # --- Regla 1: sin datos → mensaje seguro ---
    if not events and not news:
        cleaned = message.strip()
        # Si el LLM agregó contenido extra más allá de saludo+cuenta+cierre, descartar
        lines = [ln.strip() for ln in cleaned.split("\n") if ln.strip()]
        # Un mensaje básico tiene ~3 líneas: saludo, cuenta regresiva, cierre
        has_extra_content = False
        for line in lines:
            lower = line.lower()
            if any(kw in lower for kw in ["buenos días", "buen día", "faltan", "falta", "hoy comienza", "día", "coronados de gloria"]):
                continue
            # Emojis solos o líneas vacías
            if re.fullmatch(r"[\s\U0001f000-\U0001faff\u2600-\u27bf\u200d\ufe0f]*", line):
                continue
            has_extra_content = True
            break

        if has_extra_content:
            logger.warning("⚠️  Post-proceso: mensaje sin datos contenía contenido extra, reemplazando con mensaje seguro")
            return _build_safe_message(
                days_remaining, data.get("mundial_phase"), data.get("mundial_day"), weather=weather
            )

    # --- Regla 2: limpiar metadata de corchetes [Año: ...] que el LLM copió literalmente ---
    cleaned = message
    cleaned = re.sub(r"\[Año:\s*\d{4},?\s*hace\s*\d+\s*años\]\s*", "", cleaned)
    cleaned = re.sub(r"\[Año:\s*\d{4}\]\s*", "", cleaned)

    # --- Regla 3: limpiar markdown y meta-texto ---
    # Remover ** (bold markdown)
    cleaned = cleaned.replace("**", "")
    # Remover headers markdown
    for pat in _META_PATTERNS:
        cleaned = pat.sub("", cleaned)
    # Limpiar líneas vacías consecutivas
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.strip()

    # --- Regla 4: verificar años ---
    if events or news:
        allowed_years, allowed_persons, allowed_scores = _extract_allowed_entities(events, news)

        years_in_msg = {int(m) for m in re.findall(r"\b((?:19|20)\d{2})\b", cleaned)}
        hallucinated_years = years_in_msg - allowed_years
        if hallucinated_years:
            logger.warning(f"⚠️  Post-proceso: años no encontrados en datos: {hallucinated_years}")
            # Remover las oraciones con años alucinados
            for bad_year in hallucinated_years:
                # Eliminar la línea/oración que contiene el año inventado
                cleaned = re.sub(rf"[^\n]*\b{bad_year}\b[^\n]*\n?", "", cleaned)
            cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
            # Si quedó vacío tras la limpieza, usar mensaje seguro
            lines = [ln.strip() for ln in cleaned.split("\n") if ln.strip()]
            if len(lines) < 2:
                return _build_safe_message(
                    days_remaining, data.get("mundial_phase"), data.get("mundial_day"), weather=weather
                )

        # --- Regla 5: verificar scores ---
        scores_in_msg = set(re.findall(r"\b(\d+-\d+)\b", cleaned))
        hallucinated_scores = scores_in_msg - allowed_scores
        if hallucinated_scores:
            logger.warning(f"⚠️  Post-proceso: scores no encontrados en datos: {hallucinated_scores}")

    # --- Regla 6: eliminar menciones de clima escritas por el LLM (defensa;
    # el bloque de clima es 100% determinístico, ver Regla 7) ---
    cleaned = _strip_llm_weather_mentions(cleaned)

    # --- Regla 7: inyectar bloque de clima determinístico tras el countdown ---
    if weather:
        cleaned = _inject_weather_block(cleaned, weather)

    # --- Regla 8: asegurar cierre ritual ---
    if CIERRE_RITUAL.lower() not in cleaned.lower():
        logger.warning("⚠️  Post-proceso: cierre ritual faltante, agregándolo")
        cleaned = cleaned.rstrip() + f"\n\n{CIERRE_COMPLETO}"

    # Si el cierre no tiene los emojis, agregarlos
    if CIERRE_RITUAL in cleaned and "🩵🤍🩵" not in cleaned:
        cleaned = cleaned.replace(CIERRE_RITUAL, CIERRE_COMPLETO)

    # --- Regla 9: asegurar cierre doble ("Buen día" antes del cierre ritual) ---
    cleaned = _ensure_cierre_doble(cleaned)

    return cleaned


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
    
    logger.info("🚀 InforMessi - Generador de Mensajes MVP")
    logger.info("=" * 50)
    
    # Cargar datos
    data_path = Path(args.data)
    if not data_path.exists():
        logger.error(f"❌ Archivo no encontrado: {data_path}")
        sys.exit(1)
    
    logger.info(f"📂 Cargando datos: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logger.info(f"   Fecha: {data['date']}")
    logger.info(f"   Días restantes: {calculate_days_remaining(data['mundial_2026_start'], data['date'])}")
    logger.info(f"   Eventos: {len(data.get('events', []))}")
    logger.info(f"   Noticias: {len(data.get('news', []))}")
    
    llm_call = _get_llm_caller(args.provider, args.model, args.base_url)

    events = data.get("events", [])
    news = data.get("news", [])

    sys.path.insert(0, str(Path(__file__).parent))
    from llm_client import LLMClientError

    try:
        if events or news:
            logger.info("\n🔎 Seleccionando eventos y noticias relevantes...")
            selection_prompt = build_selection_prompt(data)
            selection_response = llm_call(selection_prompt, temperature=0.1, max_tokens=200)
            selected_events, selected_news = parse_selection_response(
                selection_response, events, news
            )
            logger.info(f"   Eventos seleccionados: {len(selected_events)}")
            logger.info(f"   Noticias seleccionadas: {len(selected_news)}")
        else:
            logger.info("\nℹ️  Sin eventos ni noticias, omitiendo paso de selección")
            selected_events, selected_news = [], []

        logger.info("\n📝 Construyendo prompt...")
        prompt = build_prompt(data, selected_events, selected_news)

        logger.info(f"\n🤖 Generando mensaje con {args.provider}/{args.model}...")
        logger.info("   (Esto puede tardar unos momentos...)\n")

        raw_message = llm_call(prompt)
    except LLMClientError as e:
        logger.error(f"❌ Error del cliente LLM: {e}")
        sys.exit(1)

    # Post-procesamiento: validar y limpiar
    days_remaining = calculate_days_remaining(data["mundial_2026_start"], data["date"])
    message = postprocess_message(raw_message, data, days_remaining)

    if message != raw_message:
        logger.info("🔧 Post-proceso aplicó correcciones al mensaje")

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
        logger.info(f"\n💾 Mensaje guardado en: {output_path}")
    
    # Estadísticas
    word_count = len(message.split())
    logger.info(f"\n📊 Estadísticas:")
    logger.info(f"   Palabras: {word_count}")
    logger.info(f"   Longitud objetivo: 90-130 palabras")
    if 90 <= word_count <= 130:
        logger.info("   ✅ Longitud apropiada")
    else:
        logger.warning("   ⚠️  Longitud fuera del rango objetivo")

if __name__ == "__main__":
    main()

