"""Tests for evals/checks.py — checks programáticos sobre reports generados."""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evals.checks import run_checks, summarize

REPORTS_DIR = Path(__file__).parent.parent / "reports"

gm = import_module("generate-message")
calculate_days_remaining = gm.calculate_days_remaining
format_countdown = gm.format_countdown


def _load_report(name):
    with open(REPORTS_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def _by_name(results, name):
    for r in results:
        if r["name"] == name:
            return r
    raise KeyError(f"check {name!r} not found in results")


# --- Fixture "buena": cumple la guía editorial, countdown durante el Mundial ---

GOOD_MESSAGE = """Buenos días 🇦🇷

Día 5 del Mundial 2026

🌤 Clima
AMBA: min 8° / max 16°
La Plata: min 6° / max 15°
Clima en otras partes de Argentina: https://www.smn.gob.ar/pronostico

🏆 Hoy Argentina se prepara para su próximo desafío en el Mundial 2026. La Scaloneta llega con confianza tras un arranque sólido y el país sigue de cerca cada entrenamiento buscando pistas sobre el equipo titular.

La Selección llega con la base campeona de Qatar 2022 y la ilusión de volver a lo más alto. Messi y compañía representan la mayor esperanza futbolera del país entero.

Dato del día: Estados Unidos, México y Canadá organizan el primer Mundial con 48 selecciones, el formato más grande de la historia del fútbol.

Buen día
Coronados de gloria vivamos 🩵🤍🩵"""


def make_good_report():
    return {
        "date": "2026-06-15",
        "generated_at": "2026-06-15T08:00:00-03:00",
        "data": {
            "date": "2026-06-15",
            "mundial_2026_start": "2026-06-11",
            "mundial_2026_end": "2026-07-19",
            "mundial_phase": "durante_mundial",
            "mundial_day": 5,
            "events": [],
            "news": [],
            "weather": {
                "amba": {"min": 8, "max": 16},
                "la_plata": {"min": 6, "max": 15},
                "fetched_at": "2026-06-15T07:00:00-03:00",
                "source": "open-meteo",
            },
        },
        "message": GOOD_MESSAGE,
    }


class TestGoodMessagePasses:
    def test_verdict_is_pass(self):
        report = make_good_report()
        results = run_checks(report)
        summary = summarize(results)
        failed_errors = [r for r in results if not r["passed"] and r["severity"] == "error"]
        assert failed_errors == [], f"checks de error fallados inesperadamente: {failed_errors}"
        assert summary["verdict"] == "pass"

    def test_all_checks_present(self):
        report = make_good_report()
        results = run_checks(report)
        names = {r["name"] for r in results}
        assert names == {
            "saludo",
            "countdown_correcto",
            "clima_presente",
            "sin_placeholders",
            "cierre_ritual",
            "años_grounded",
            "fecha_correcta",
            "longitud",
            "sin_markdown",
            "emojis",
        }


class TestSaludo:
    def test_pass(self):
        report = make_good_report()
        result = _by_name(run_checks(report), "saludo")
        assert result["passed"] is True
        assert result["severity"] == "error"

    def test_fail_sin_bandera(self):
        report = make_good_report()
        report["message"] = report["message"].replace("Buenos días 🇦🇷", "Buenos días")
        result = _by_name(run_checks(report), "saludo")
        assert result["passed"] is False

    def test_fail_sin_saludo(self):
        report = make_good_report()
        report["message"] = "Hola a todos 🇦🇷\n\n" + report["message"]
        result = _by_name(run_checks(report), "saludo")
        assert result["passed"] is False

    def test_pass_buen_dia_variant(self):
        report = make_good_report()
        report["message"] = report["message"].replace("Buenos días 🇦🇷", "Buen día 🇦🇷")
        result = _by_name(run_checks(report), "saludo")
        assert result["passed"] is True


class TestCountdownCorrecto:
    def test_pass_durante_mundial(self):
        report = make_good_report()
        result = _by_name(run_checks(report), "countdown_correcto")
        assert result["passed"] is True

    def test_fail_wrong_day(self):
        report = make_good_report()
        report["message"] = report["message"].replace("Día 5 del Mundial 2026", "Día 9 del Mundial 2026")
        result = _by_name(run_checks(report), "countdown_correcto")
        assert result["passed"] is False

    def test_pass_antes_del_mundial(self):
        report = make_good_report()
        report["date"] = "2026-06-01"
        report["data"]["date"] = "2026-06-01"
        report["data"]["mundial_phase"] = None
        report["data"]["mundial_day"] = None
        days = calculate_days_remaining("2026-06-11", "2026-06-01")
        expected = format_countdown(days, None, None)
        report["message"] = report["message"].replace("Día 5 del Mundial 2026", expected)
        result = _by_name(run_checks(report), "countdown_correcto")
        assert result["passed"] is True

    def test_fail_antes_del_mundial_frase_de_durante(self):
        report = make_good_report()
        report["date"] = "2026-06-01"
        report["data"]["date"] = "2026-06-01"
        report["data"]["mundial_phase"] = None
        report["data"]["mundial_day"] = None
        # el mensaje sigue diciendo "Día 5 del Mundial 2026" (frase de durante el Mundial),
        # que no corresponde a esta fecha (antes de que arranque)
        result = _by_name(run_checks(report), "countdown_correcto")
        assert result["passed"] is False


class TestClimaPresente:
    def test_pass_matching(self):
        report = make_good_report()
        result = _by_name(run_checks(report), "clima_presente")
        assert result["passed"] is True

    def test_skip_sin_weather(self):
        report = make_good_report()
        report["data"].pop("weather")
        # eliminar el bloque de clima del mensaje también, no debería importar
        result = _by_name(run_checks(report), "clima_presente")
        assert result["passed"] is True
        assert "skip" in result["detail"].lower()

    def test_fail_temperatura_no_coincide(self):
        report = make_good_report()
        report["message"] = report["message"].replace("AMBA: min 8° / max 16°", "AMBA: min 99° / max 16°")
        result = _by_name(run_checks(report), "clima_presente")
        assert result["passed"] is False

    def test_fail_bloque_ausente(self):
        report = make_good_report()
        lines = [ln for ln in report["message"].split("\n") if "Clima" not in ln and "AMBA" not in ln and "La Plata" not in ln]
        report["message"] = "\n".join(lines)
        result = _by_name(run_checks(report), "clima_presente")
        assert result["passed"] is False


class TestSinPlaceholders:
    def test_pass(self):
        report = make_good_report()
        result = _by_name(run_checks(report), "sin_placeholders")
        assert result["passed"] is True

    def test_fail_doble_espacio_placeholder(self):
        report = make_good_report()
        report["message"] += "\n\nHoy Argentina enfrenta a  en el  a las 16:00."
        result = _by_name(run_checks(report), "sin_placeholders")
        assert result["passed"] is False

    def test_fail_underscore(self):
        report = make_good_report()
        report["message"] += "\n\nEsto tiene un __ placeholder."
        result = _by_name(run_checks(report), "sin_placeholders")
        assert result["passed"] is False

    def test_fail_none_literal(self):
        report = make_good_report()
        report["message"] += "\n\nEl rival es None por ahora."
        result = _by_name(run_checks(report), "sin_placeholders")
        assert result["passed"] is False

    def test_fail_llaves(self):
        report = make_good_report()
        report["message"] += "\n\nDato: {placeholder}"
        result = _by_name(run_checks(report), "sin_placeholders")
        assert result["passed"] is False

    def test_regression_report_2026_06_28(self):
        """Report real de producción con placeholder 'enfrenta a  en el  a las 16:00'."""
        report = _load_report("2026-06-28.json")
        result = _by_name(run_checks(report), "sin_placeholders")
        assert result["passed"] is False


class TestCierreRitual:
    def test_pass(self):
        report = make_good_report()
        result = _by_name(run_checks(report), "cierre_ritual")
        assert result["passed"] is True

    def test_fail_sin_buen_dia(self):
        report = make_good_report()
        report["message"] = report["message"].replace("Buen día\nCoronados de gloria vivamos 🩵🤍🩵", "Coronados de gloria vivamos 🩵🤍🩵")
        result = _by_name(run_checks(report), "cierre_ritual")
        assert result["passed"] is False

    def test_fail_sin_frase_ritual(self):
        report = make_good_report()
        report["message"] = report["message"].replace("Coronados de gloria vivamos 🩵🤍🩵", "Nos vemos mañana 🩵🤍🩵")
        result = _by_name(run_checks(report), "cierre_ritual")
        assert result["passed"] is False

    def test_regression_report_2026_06_27_sin_buen_dia(self):
        """Report real que termina directo en la frase ritual, sin línea 'Buen día' previa."""
        report = _load_report("2026-06-27.json")
        result = _by_name(run_checks(report), "cierre_ritual")
        assert result["passed"] is False


class TestAniosGrounded:
    def test_pass_sin_anios_mencionados(self):
        report = make_good_report()
        result = _by_name(run_checks(report), "años_grounded")
        assert result["passed"] is True

    def test_pass_anio_permitido(self):
        report = make_good_report()
        report["message"] = report["message"].replace("Qatar 2022", "Qatar 2022 (2022)")
        result = _by_name(run_checks(report), "años_grounded")
        assert result["passed"] is True

    def test_fail_anio_alucinado(self):
        report = make_good_report()
        report["message"] += "\n\nEn 1999 pasó algo memorable que no está en los datos."
        result = _by_name(run_checks(report), "años_grounded")
        assert result["passed"] is False


class TestFechaCorrecta:
    def test_pass_sin_expected_date(self):
        report = make_good_report()
        result = _by_name(run_checks(report), "fecha_correcta")
        assert result["passed"] is True

    def test_pass_expected_date_matches(self):
        report = make_good_report()
        result = _by_name(run_checks(report, expected_date="2026-06-15"), "fecha_correcta")
        assert result["passed"] is True

    def test_fail_expected_date_mismatch(self):
        report = make_good_report()
        result = _by_name(run_checks(report, expected_date="2026-06-16"), "fecha_correcta")
        assert result["passed"] is False

    def test_fail_claude_agent_generated_at_mismatch(self):
        report = make_good_report()
        report["source"] = "claude-agent"
        report["generated_at"] = "2026-06-16T08:00:00-03:00"
        result = _by_name(run_checks(report), "fecha_correcta")
        assert result["passed"] is False

    def test_pass_claude_agent_generated_at_matches(self):
        report = make_good_report()
        report["source"] = "claude-agent"
        report["generated_at"] = "2026-06-15T08:00:00-03:00"
        result = _by_name(run_checks(report), "fecha_correcta")
        assert result["passed"] is True


class TestLongitud:
    def test_pass_en_rango(self):
        report = make_good_report()
        result = _by_name(run_checks(report), "longitud")
        assert result["passed"] is True
        assert result["severity"] == "error"  # dentro del rango no se evalúa severidad de falla

    def test_warning_corto(self):
        report = make_good_report()
        report["message"] = " ".join(["palabra"] * 70)
        result = _by_name(run_checks(report), "longitud")
        assert result["passed"] is False
        assert result["severity"] == "warning"

    def test_error_muy_corto(self):
        report = make_good_report()
        report["message"] = " ".join(["palabra"] * 40)
        result = _by_name(run_checks(report), "longitud")
        assert result["passed"] is False
        assert result["severity"] == "error"

    def test_warning_largo(self):
        report = make_good_report()
        report["message"] = " ".join(["palabra"] * 165)
        result = _by_name(run_checks(report), "longitud")
        assert result["passed"] is False
        assert result["severity"] == "warning"

    def test_error_muy_largo(self):
        report = make_good_report()
        report["message"] = " ".join(["palabra"] * 190)
        result = _by_name(run_checks(report), "longitud")
        assert result["passed"] is False
        assert result["severity"] == "error"


class TestSinMarkdown:
    def test_pass(self):
        report = make_good_report()
        result = _by_name(run_checks(report), "sin_markdown")
        assert result["passed"] is True
        assert result["severity"] == "warning"

    def test_fail_bold(self):
        report = make_good_report()
        report["message"] = report["message"].replace("Buenos días", "**Buenos días**")
        result = _by_name(run_checks(report), "sin_markdown")
        assert result["passed"] is False

    def test_fail_header(self):
        report = make_good_report()
        report["message"] = "## Titulo\n" + report["message"]
        result = _by_name(run_checks(report), "sin_markdown")
        assert result["passed"] is False

    def test_fail_codeblock(self):
        report = make_good_report()
        report["message"] += "\n```codigo```"
        result = _by_name(run_checks(report), "sin_markdown")
        assert result["passed"] is False


class TestEmojis:
    def test_pass(self):
        report = make_good_report()
        result = _by_name(run_checks(report), "emojis")
        assert result["passed"] is True
        assert result["severity"] == "warning"
        # GOOD_MESSAGE contiene: 1 bandera (🇦🇷) + 5 otros emojis (🌤🏆🩵🤍🩵) = 6 total
        assert "6 emojis" in result["detail"]

    def test_fail_sin_emojis(self):
        report = make_good_report()
        import re
        emoji_pattern = re.compile(
            "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]"
        )
        report["message"] = emoji_pattern.sub("", report["message"])
        result = _by_name(run_checks(report), "emojis")
        assert result["passed"] is False

    def test_fail_demasiados_emojis(self):
        report = make_good_report()
        # Agregar emojis: ⚽🎉🎊🏆🥳🔥✨ (7 no-banderas) + 🇦🇷 (1 bandera)
        # = 8 emojis totales, fuera del rango 3-7
        report["message"] += "\n" + "⚽🎉🎊🏆🥳🔥✨🇦🇷"
        result = _by_name(run_checks(report), "emojis")
        assert result["passed"] is False
        # Resultado esperado: 6 (original) + 8 (agregados) = 14
        # Realmente: 6 + 1 bandera + 7 otros = 14
        assert "14 emojis" in result["detail"]


class TestSummarize:
    def test_all_pass(self):
        report = make_good_report()
        results = run_checks(report)
        summary = summarize(results)
        assert summary["verdict"] in ("pass", "pass_with_warnings")
        assert summary["errors_failed"] == 0

    def test_fail_verdict_when_error_fails(self):
        report = make_good_report()
        report["message"] = report["message"].replace("Coronados de gloria vivamos 🩵🤍🩵", "Nos vemos 🩵🤍🩵")
        results = run_checks(report)
        summary = summarize(results)
        assert summary["verdict"] == "fail"
        assert summary["errors_failed"] >= 1

    def test_pass_with_warnings_verdict(self):
        report = make_good_report()
        # Mensaje corto (65 palabras, rango warning 60-89) pero que conserva saludo,
        # countdown, clima y cierre correctos, para aislar el warning de longitud.
        report["message"] = (
            "Buenos días 🇦🇷\n\n"
            "Día 5 del Mundial 2026\n\n"
            "🌤 Clima\n"
            "AMBA: min 8° / max 16°\n"
            "La Plata: min 6° / max 15°\n"
            "Clima en otras partes de Argentina: https://www.smn.gob.ar/pronostico\n\n"
            "🏆 Hoy Argentina se prepara para su próximo desafío en el Mundial 2026 con confianza. "
            "La Scaloneta sigue de cerca cada entrenamiento buscando pistas sobre el equipo titular.\n\n"
            "Buen día\n"
            "Coronados de gloria vivamos 🩵🤍🩵"
        )
        results = run_checks(report)
        summary = summarize(results)
        assert summary["verdict"] == "pass_with_warnings"
        assert summary["errors_failed"] == 0
        assert summary["warnings_failed"] >= 1

    def test_summary_has_passed_count(self):
        report = make_good_report()
        results = run_checks(report)
        summary = summarize(results)
        assert summary["passed"] == sum(1 for r in results if r["passed"])
