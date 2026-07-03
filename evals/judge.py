"""LLM-as-judge para InforMessi.

judge_message(message, data) llama a Groq con prompts/judge-prompt.md como
system prompt para evaluar un mensaje generado contra la guía editorial y
los datos fuente del día. Es best-effort: cualquier error (API caída, JSON
inválido) devuelve None en vez de romper el pipeline.
"""

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from llm_client import call_groq  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

JUDGE_PROMPT_PATH = ROOT / "prompts" / "judge-prompt.md"

_DIMENSIONS = ("tono", "estructura", "fidelidad_guia", "factualidad_aparente")


def _load_system_prompt() -> str:
    return JUDGE_PROMPT_PATH.read_text(encoding="utf-8")


def _build_user_prompt(message: str, data: dict) -> str:
    data = data or {}
    compact_data = {
        "events": data.get("events", []),
        "news": data.get("news", []),
        "weather": data.get("weather", {}),
    }
    return (
        "Mensaje a evaluar:\n"
        f"{message}\n\n"
        "Datos fuente (evaluar el mensaje SOLO contra esto):\n"
        f"{json.dumps(compact_data, ensure_ascii=False)}"
    )


def _parse_and_validate(raw: str) -> dict | None:
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None

    if not isinstance(parsed, dict):
        return None

    scores = {}
    for dim in _DIMENSIONS:
        value = parsed.get(dim)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return None
        if not (1 <= value <= 5):
            return None
        scores[dim] = value

    scores["comentario"] = parsed.get("comentario", "")
    return scores


def judge_message(message: str, data: dict, model: str = "llama-3.3-70b-versatile") -> dict | None:
    """Evalúa `message` contra `data` (fuentes) usando un LLM judge.

    Retorna un dict con las 4 dimensiones (1-5), "comentario", "promedio"
    (redondeado a 2 decimales) y "model". Retorna None ante cualquier error:
    API caída, respuesta no-JSON, JSON con dimensiones faltantes/fuera de
    rango (sin reintento real de red, solo se reintenta el parseo si hace
    falta extraer el JSON de texto extra).
    """
    try:
        system = _load_system_prompt()
        user_prompt = _build_user_prompt(message, data)

        raw = call_groq(
            user_prompt,
            model=model,
            temperature=0,
            max_tokens=400,
            json_mode=True,
            system=system,
        )
    except Exception as e:
        logger.warning(f"judge_message: error llamando a Groq: {e}")
        return None

    result = _parse_and_validate(raw)
    if result is None:
        # Reintento de parseo: extraer el primer bloque {...} del texto,
        # por si el modelo agregó texto alrededor del JSON.
        start = raw.find("{") if isinstance(raw, str) else -1
        end = raw.rfind("}") if isinstance(raw, str) else -1
        if start != -1 and end != -1 and end > start:
            result = _parse_and_validate(raw[start:end + 1])

    if result is None:
        logger.warning(f"judge_message: JSON inválido o incompleto tras reintento: {raw!r}")
        return None

    promedio = round(sum(result[dim] for dim in _DIMENSIONS) / len(_DIMENSIONS), 2)
    result["promedio"] = promedio
    result["model"] = model
    return result
