"""Checks programáticos sobre un report de InforMessi.

Cada check valida una regla de docs/editorial-guide.md contra
report["message"] (y, cuando corresponde, report["data"]).

run_checks(report, expected_date=None) -> list[dict]
    Cada resultado: {"name": str, "passed": bool, "severity": "error"|"warning", "detail": str}

summarize(results) -> dict
    {"passed": int, "errors_failed": int, "warnings_failed": int, "verdict": str}
"""

import re
import sys
from importlib import import_module
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# generate-message.py tiene guion en el nombre: import vía importlib
# (mismo patrón que tests/test_generate_message.py).
_gm = import_module("generate-message")
calculate_days_remaining = _gm.calculate_days_remaining
format_countdown = _gm.format_countdown
_extract_allowed_entities = _gm._extract_allowed_entities

from time_utils import parse_ts, TZ_AR  # noqa: E402


# --- Regex / constantes compartidas ---

_SALUDO_RE = re.compile(r"^Buen(os)? día(s)?", re.IGNORECASE)
_BANDERA_AR = "🇦🇷"

_PLACEHOLDER_PATTERNS = [
    re.compile(r"__"),
    re.compile(r"\[Año:"),
    re.compile(r"\{[^}]*\}"),
    re.compile(r"enfrenta a\s+en"),
    re.compile(r"\ben el\s+a las"),
    re.compile(r"\s{2,}[.,]"),
    re.compile(r"\bNone\b"),
    re.compile(r"\bnull\b", re.IGNORECASE),
]

CIERRE_RITUAL = "Coronados de gloria vivamos"

_MARKDOWN_PATTERNS = [
    re.compile(r"\*\*"),
    re.compile(r"##"),
    re.compile(r"```"),
]

# Rangos unicode típicos de emoji (simplificado, cubre los usados en el proyecto:
# emoticons, símbolos misceláneos, dingbats, banderas regionales, transporte).
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"  # símbolos misc, emoticons, transporte, suplementarios
    "\U00002600-\U000027BF"  # misc symbols y dingbats
    "\U0001F1E6-\U0001F1FF"  # regional indicators (banderas)
    "\U0000FE0F"             # variation selector (emoji presentation)
    "]"
)

_YEAR_RE = re.compile(r"\b((?:19|20)\d{2})\b")


def _make_result(name, passed, severity, detail):
    return {"name": name, "passed": passed, "severity": severity, "detail": detail}


def _non_empty_lines(message):
    return [ln.strip() for ln in message.split("\n") if ln.strip()]


# --- Checks individuales ---

def check_saludo(report):
    message = report.get("message", "")
    lines = _non_empty_lines(message)
    if not lines:
        return _make_result("saludo", False, "error", "Mensaje vacío, no hay saludo.")
    first = lines[0]
    if not _SALUDO_RE.match(first):
        return _make_result(
            "saludo", False, "error",
            f"Primera línea no matchea /^Buen(os)? día(s)?/: {first!r}"
        )
    if _BANDERA_AR not in first:
        return _make_result(
            "saludo", False, "error",
            f"Primera línea no contiene {_BANDERA_AR}: {first!r}"
        )
    return _make_result("saludo", True, "error", "Saludo correcto.")


def check_countdown_correcto(report):
    message = report.get("message", "")
    data = report.get("data", {}) or {}
    report_date = report.get("date")

    mundial_start = data.get("mundial_2026_start")
    if not report_date or not mundial_start:
        return _make_result(
            "countdown_correcto", False, "error",
            "Falta report['date'] o data['mundial_2026_start'] para calcular el countdown."
        )

    days_remaining = calculate_days_remaining(mundial_start, report_date)
    expected = format_countdown(
        days_remaining,
        data.get("mundial_phase"),
        data.get("mundial_day"),
    )

    if expected in message:
        return _make_result("countdown_correcto", True, "error", f"Countdown correcto: {expected!r}")
    return _make_result(
        "countdown_correcto", False, "error",
        f"El mensaje no contiene la frase de countdown esperada {expected!r} para date={report_date}."
    )


def check_clima_presente(report):
    data = report.get("data", {}) or {}
    weather = data.get("weather")
    message = report.get("message", "")

    if not weather:
        return _make_result("clima_presente", True, "error", "sin datos de clima (skip)")

    amba = weather.get("amba", {}) or {}
    la_plata = weather.get("la_plata", {}) or {}

    if "Clima" not in message or "AMBA" not in message or "La Plata" not in message:
        return _make_result(
            "clima_presente", False, "error",
            "El mensaje no contiene el bloque de clima (Clima/AMBA/La Plata)."
        )

    amba_re = re.search(r"AMBA:\s*min\s*(-?\d+)°?\s*/\s*max\s*(-?\d+)°?", message)
    la_plata_re = re.search(r"La Plata:\s*min\s*(-?\d+)°?\s*/\s*max\s*(-?\d+)°?", message)

    if not amba_re or not la_plata_re:
        return _make_result(
            "clima_presente", False, "error",
            "No se pudieron extraer las temperaturas AMBA/La Plata del mensaje."
        )

    amba_min, amba_max = int(amba_re.group(1)), int(amba_re.group(2))
    lp_min, lp_max = int(la_plata_re.group(1)), int(la_plata_re.group(2))

    mismatches = []
    if amba.get("min") != amba_min:
        mismatches.append(f"AMBA min esperado {amba.get('min')} != {amba_min}")
    if amba.get("max") != amba_max:
        mismatches.append(f"AMBA max esperado {amba.get('max')} != {amba_max}")
    if la_plata.get("min") != lp_min:
        mismatches.append(f"La Plata min esperado {la_plata.get('min')} != {lp_min}")
    if la_plata.get("max") != lp_max:
        mismatches.append(f"La Plata max esperado {la_plata.get('max')} != {lp_max}")

    if mismatches:
        return _make_result("clima_presente", False, "error", "; ".join(mismatches))
    return _make_result("clima_presente", True, "error", "Bloque de clima presente y temperaturas coinciden.")


def check_sin_placeholders(report):
    message = report.get("message", "")
    hits = []
    for pattern in _PLACEHOLDER_PATTERNS:
        m = pattern.search(message)
        if m:
            hits.append(f"{pattern.pattern!r} -> {m.group(0)!r}")
    if hits:
        return _make_result("sin_placeholders", False, "error", "Placeholders encontrados: " + "; ".join(hits))
    return _make_result("sin_placeholders", True, "error", "Sin placeholders.")


def check_cierre_ritual(report):
    message = report.get("message", "")
    lines = _non_empty_lines(message)
    if len(lines) < 2:
        return _make_result("cierre_ritual", False, "error", "Mensaje demasiado corto para tener cierre.")

    penultima = lines[-2]
    ultima = lines[-1]

    penultima_ok = penultima == "Buen día" or penultima.startswith("Buen día")
    ultima_ok = "Coronados de gloria vivamos" in ultima

    if penultima_ok and ultima_ok:
        return _make_result("cierre_ritual", True, "error", "Cierre ritual correcto.")

    problems = []
    if not penultima_ok:
        problems.append(f"anteúltima línea no es 'Buen día': {penultima!r}")
    if not ultima_ok:
        problems.append(f"última línea no contiene la frase ritual: {ultima!r}")
    return _make_result("cierre_ritual", False, "error", "; ".join(problems))


def check_años_grounded(report):
    message = report.get("message", "")
    data = report.get("data", {}) or {}
    report_date = report.get("date", "")

    events = data.get("events", []) or []
    news = data.get("news", []) or []

    allowed_years, _, _ = _extract_allowed_entities(events, news)

    if report_date and len(report_date) >= 4:
        try:
            allowed_years.add(int(report_date[:4]))
        except ValueError:
            pass
    allowed_years.add(2026)

    years_in_msg = {int(m) for m in _YEAR_RE.findall(message)}
    hallucinated = years_in_msg - allowed_years

    if hallucinated:
        return _make_result(
            "años_grounded", False, "error",
            f"Años mencionados no presentes en datos permitidos: {sorted(hallucinated)}"
        )
    return _make_result("años_grounded", True, "error", "Todos los años mencionados están grounded en los datos.")


def check_fecha_correcta(report, expected_date=None):
    report_date = report.get("date")

    if expected_date is not None and report_date != expected_date:
        return _make_result(
            "fecha_correcta", False, "error",
            f"report['date']={report_date!r} != expected_date={expected_date!r}"
        )

    if report.get("source") == "claude-agent":
        generated_at = report.get("generated_at")
        if not generated_at:
            return _make_result(
                "fecha_correcta", False, "error",
                "source=claude-agent pero falta generated_at."
            )
        try:
            generated_date = parse_ts(generated_at).astimezone(TZ_AR).date().isoformat()
        except (ValueError, TypeError) as e:
            return _make_result(
                "fecha_correcta", False, "error",
                f"No se pudo parsear generated_at={generated_at!r}: {e}"
            )
        if generated_date != report_date:
            return _make_result(
                "fecha_correcta", False, "error",
                f"generated_at ({generated_date}, TZ AR) != report['date'] ({report_date})"
            )

    return _make_result("fecha_correcta", True, "error", "Fecha correcta.")


def check_longitud(report):
    message = report.get("message", "")
    word_count = len(message.split())

    if 90 <= word_count <= 150:
        return _make_result("longitud", True, "error", f"{word_count} palabras, dentro de 90-150.")
    if 60 <= word_count <= 89 or 151 <= word_count <= 180:
        return _make_result("longitud", False, "warning", f"{word_count} palabras, fuera del rango ideal (90-150).")
    return _make_result("longitud", False, "error", f"{word_count} palabras, fuera de rango aceptable (<60 o >180).")


def check_sin_markdown(report):
    message = report.get("message", "")
    hits = [p.pattern for p in _MARKDOWN_PATTERNS if p.search(message)]
    if hits:
        return _make_result("sin_markdown", False, "warning", "Markdown encontrado: " + ", ".join(hits))
    return _make_result("sin_markdown", True, "warning", "Sin markdown.")


def check_emojis(report):
    message = report.get("message", "")
    # Contar pares de regional indicators (banderas) como 1 emoji cada uno
    # Ejemplo: 🇦🇷 = U+1F1E6 + U+1F1F7 = se cuenta como 1 emoji visual
    flag_pattern = re.compile(r'[\U0001F1E6-\U0001F1FF]{2}')
    flags = flag_pattern.findall(message)
    flag_count = len(flags)

    # Eliminar las banderas del texto para contar el resto de emojis
    message_without_flags = flag_pattern.sub('', message)

    # Contar emojis restantes (sin el rango de regional indicators que ya contamos)
    rest_emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001FAFF"  # símbolos misc, emoticons, transporte, suplementarios
        "\U00002600-\U000027BF"  # misc symbols y dingbats
        "\U0000FE0F"             # variation selector (emoji presentation)
        "]"
    )
    rest_count = len(rest_emoji_pattern.findall(message_without_flags))
    count = flag_count + rest_count

    if 3 <= count <= 7:
        return _make_result("emojis", True, "warning", f"{count} emojis, dentro de 3-7.")
    return _make_result("emojis", False, "warning", f"{count} emojis, fuera de 3-7.")


_ALL_CHECKS = [
    check_saludo,
    check_countdown_correcto,
    check_clima_presente,
    check_sin_placeholders,
    check_cierre_ritual,
    check_años_grounded,
    check_longitud,
    check_sin_markdown,
    check_emojis,
]


def run_checks(report: dict, expected_date: str | None = None) -> list:
    """Corre todos los checks programáticos sobre un report. Retorna lista de resultados."""
    results = [check(report) for check in _ALL_CHECKS]
    results.append(check_fecha_correcta(report, expected_date=expected_date))
    return results


def summarize(results: list) -> dict:
    """Resume una lista de resultados de checks en un veredicto único."""
    passed = sum(1 for r in results if r["passed"])
    errors_failed = sum(1 for r in results if not r["passed"] and r["severity"] == "error")
    warnings_failed = sum(1 for r in results if not r["passed"] and r["severity"] == "warning")

    if errors_failed > 0:
        verdict = "fail"
    elif warnings_failed > 0:
        verdict = "pass_with_warnings"
    else:
        verdict = "pass"

    return {
        "passed": passed,
        "errors_failed": errors_failed,
        "warnings_failed": warnings_failed,
        "verdict": verdict,
    }
