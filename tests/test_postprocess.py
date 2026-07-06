"""Tests for postprocess_message() en generate-message.py:
inyeccion deterministica del bloque de clima, cierre doble
("Buen dia" + "Coronados de gloria vivamos"), y contrato
integrador con evals.checks.run_checks.
"""

import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

gm = import_module("generate-message")
postprocess_message = gm.postprocess_message

from evals.checks import run_checks, summarize  # noqa: E402


SALUDO = "Buenos d" + chr(0xED) + "as " + chr(0x1F1E6) + chr(0x1F1F7)
DIA5 = "D" + chr(0xED) + "a 5 del Mundial 2026"
BUEN_DIA = "Buen d" + chr(0xED) + "a"
CIERRE = "Coronados de gloria vivamos " + chr(0x1FA75) + chr(0x1F90D) + chr(0x1FA75)
NL = chr(10)

WEATHER = {
    "amba": {"min": 8, "max": 16},
    "la_plata": {"min": 6, "max": 15},
    "fetched_at": "2026-06-15T07:00:00-03:00",
    "source": "open-meteo",
}

SOME_EVENT = [
    {
        "type": "generic",
        "date": "1978-06-25",
        "description": "Argentina se consagro campeon del Mundial 1978 ante Holanda.",
    }
]


def _base_data(**overrides):
    data = {
        "date": "2026-06-15",
        "mundial_2026_start": "2026-06-11",
        "mundial_2026_end": "2026-07-19",
        "mundial_phase": "durante_mundial",
        "mundial_day": 5,
        "events": [],
        "news": [],
    }
    data.update(overrides)
    return data


def _join(*parts):
    return (NL + NL).join(parts)


class TestInyeccionClima:
    def test_bloque_clima_aparece_despues_del_countdown(self):
        raw = _join(
            SALUDO,
            DIA5,
            "La Scaloneta sigue firme en el Mundial 2026, con Messi liderando "
            "al equipo hacia la siguiente fase con confianza total.",
            BUEN_DIA + NL + CIERRE,
        )
        data = _base_data(weather=WEATHER, events=SOME_EVENT)
        result = postprocess_message(raw, data, days_remaining=-4)

        lines = [ln for ln in result.split(NL) if ln.strip()]
        countdown_idx = next(i for i, ln in enumerate(lines) if ln == DIA5)
        assert lines[countdown_idx + 1] == "\U0001F324 Clima"
        assert "AMBA: min 8" in result
        assert "La Plata: min 6" in result

    def test_sin_weather_no_hay_bloque_clima(self):
        raw = _join(
            SALUDO,
            DIA5,
            "La Scaloneta sigue firme en el Mundial 2026, con Messi liderando "
            "al equipo hacia la siguiente fase con confianza total.",
            BUEN_DIA + NL + CIERRE,
        )
        data = _base_data(events=SOME_EVENT)  # sin weather
        result = postprocess_message(raw, data, days_remaining=-4)

        assert "Clima" not in result
        assert "AMBA" not in result

    def test_sin_linea_countdown_se_inserta_tras_saludo(self):
        # El countdown no matchea textualmente la frase esperada (ej. LLM la altero);
        # el bloque de clima debe insertarse tras la primera linea (saludo).
        raw = _join(
            SALUDO,
            "Estamos en pleno Mundial 2026",
            BUEN_DIA + NL + CIERRE,
        )
        data = _base_data(weather=WEATHER, events=SOME_EVENT)
        result = postprocess_message(raw, data, days_remaining=-4)

        lines = [ln for ln in result.split(NL) if ln.strip()]
        assert lines[0] == SALUDO
        assert lines[1] == "\U0001F324 Clima"

    def test_elimina_linea_de_clima_escrita_por_el_llm(self):
        raw = _join(
            SALUDO,
            DIA5,
            "Hoy se espera un clima fresco en Buenos Aires, con minima de 8 y maxima de 16 grados.",
            "La Scaloneta sigue firme en el Mundial 2026, con Messi liderando "
            "al equipo hacia la siguiente fase con confianza total.",
            BUEN_DIA + NL + CIERRE,
        )
        data = _base_data(weather=WEATHER, events=SOME_EVENT)
        result = postprocess_message(raw, data, days_remaining=-4)

        assert "grados" not in result.lower()
        assert "clima fresco" not in result.lower()
        # El bloque deterministico sigue presente
        assert "\U0001F324 Clima" in result
        assert result.count("\U0001F324 Clima") == 1

    def test_no_elimina_falso_positivo_clima_tenso(self):
        # "clima" en sentido figurado (ambiente del vestuario), no meteorologico.
        raw = _join(
            SALUDO,
            DIA5,
            "El clima tenso del vestuario preocupa a Scaloni de cara al proximo partido "
            "del equipo en el Mundial 2026.",
            BUEN_DIA + NL + CIERRE,
        )
        data = _base_data(weather=WEATHER, events=SOME_EVENT)
        result = postprocess_message(raw, data, days_remaining=-4)

        assert "clima tenso" in result.lower()

    def test_no_elimina_falso_positivo_grados_ranking(self):
        # "grados" en un sentido no meteorologico (diferencia de puntos/ranking).
        raw = _join(
            SALUDO,
            DIA5,
            "La Scaloneta gano por 30 grados de diferencia en el ranking FIFA "
            "respecto de su rival de turno.",
            BUEN_DIA + NL + CIERRE,
        )
        data = _base_data(weather=WEATHER, events=SOME_EVENT)
        result = postprocess_message(raw, data, days_remaining=-4)

        assert "30 grados de diferencia" in result.lower()

    def test_elimina_linea_con_emoji_sol_y_grados_maxima(self):
        raw = _join(
            SALUDO,
            DIA5,
            "☀️ Hoy 25 grados de maxima en Buenos Aires",
            "La Scaloneta sigue firme en el Mundial 2026, con Messi liderando "
            "al equipo hacia la siguiente fase con confianza total.",
            BUEN_DIA + NL + CIERRE,
        )
        data = _base_data(weather=WEATHER, events=SOME_EVENT)
        result = postprocess_message(raw, data, days_remaining=-4)

        assert "25 grados de maxima" not in result.lower()

    def test_elimina_linea_con_pronostico_y_grado_minima(self):
        raw = _join(
            SALUDO,
            DIA5,
            "El pronostico anuncia 12° de minima para hoy en la ciudad.",
            "La Scaloneta sigue firme en el Mundial 2026, con Messi liderando "
            "al equipo hacia la siguiente fase con confianza total.",
            BUEN_DIA + NL + CIERRE,
        )
        data = _base_data(weather=WEATHER, events=SOME_EVENT)
        result = postprocess_message(raw, data, days_remaining=-4)

        assert "12° de minima" not in result.lower()


class TestCierreDoble:
    def test_inserta_buen_dia_si_falta(self):
        raw = _join(
            SALUDO,
            DIA5,
            "La Scaloneta sigue firme en el Mundial 2026, con Messi liderando "
            "al equipo hacia la siguiente fase con confianza total.",
            CIERRE,
        )
        data = _base_data(events=SOME_EVENT)
        result = postprocess_message(raw, data, days_remaining=-4)

        lines = [ln for ln in result.split(NL) if ln.strip()]
        assert lines[-2] == BUEN_DIA
        assert CIERRE in lines[-1]

    def test_no_duplica_buen_dia_si_ya_existe(self):
        raw = _join(
            SALUDO,
            DIA5,
            "La Scaloneta sigue firme en el Mundial 2026, con Messi liderando "
            "al equipo hacia la siguiente fase con confianza total.",
            BUEN_DIA + NL + CIERRE,
        )
        data = _base_data(events=SOME_EVENT)
        result = postprocess_message(raw, data, days_remaining=-4)

        assert result.count(BUEN_DIA) == 1


class TestIntegracionConChecks:
    def test_mensaje_postprocesado_pasa_run_checks(self):
        """Contrato de la tarea: mensaje sintetico crudo del LLM + data con
        weather -> postprocess produce un mensaje que pasa evals.checks.run_checks
        con verdict pass (o pass_with_warnings, nunca fail)."""
        events = [
            {
                "type": "generic",
                "date": "1978-06-25",
                "description": "Argentina se consagro campeon del Mundial 1978 ante Holanda.",
            }
        ]
        raw = _join(
            SALUDO,
            DIA5,
            "\U0001F3C6 Hoy Argentina se prepara para su proximo desafio en el Mundial 2026. "
            "La Scaloneta llega con confianza tras un arranque solido y el pais entero "
            "sigue de cerca cada entrenamiento buscando pistas sobre el equipo titular.",
            "La Seleccion llega con la base campeona de Qatar 2022 y la ilusion de volver "
            "a lo mas alto. Messi y compania representan la mayor esperanza futbolera del pais.",
            "Dato del dia: hace 48 anios, Argentina goleo en el Mundial 1978 y se corono campeon "
            "por primera vez en su historia, un antecedente que la Scaloneta busca igualar.",
            CIERRE,
        )
        data = _base_data(weather=WEATHER, events=events)
        days_remaining = -4  # Dia 5 del Mundial (mundial_day=5)

        message = postprocess_message(raw, data, days_remaining)

        report = {
            "date": "2026-06-15",
            "generated_at": "2026-06-15T08:00:00-03:00",
            "data": data,
            "message": message,
        }

        results = run_checks(report)
        summary = summarize(results)
        failed_errors = [r for r in results if not r["passed"] and r["severity"] == "error"]

        assert failed_errors == [], "checks de error fallados: %r" % (failed_errors,)
        assert summary["verdict"] in ("pass", "pass_with_warnings")
