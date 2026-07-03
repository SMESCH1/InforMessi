"""Tests para la lógica de dedup/replace de add-mundial-fixture.py."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from importlib import import_module

amf = import_module("add-mundial-fixture")

apply_fixture = amf.apply_fixture


def _write_events(tmp_path, events):
    events_file = tmp_path / "events.json"
    events_file.write_text(
        json.dumps({"description": "test", "schema_version": "1.0", "events": events},
                   ensure_ascii=False),
        encoding="utf-8",
    )
    return events_file


def _read_events(events_file):
    return json.loads(events_file.read_text(encoding="utf-8"))["events"]


FIXTURE = [
    {
        "date": "2026-07-03",
        "type": "match",
        "priority": "critical",
        "person": "Selección Argentina",
        "description": "Mundial 2026 - Dieciseisavos: Argentina vs Cabo Verde.",
    },
    {
        "date": "2026-07-19",
        "type": "match",
        "priority": "critical",
        "person": "N/A",
        "description": "FINAL del Mundial 2026, MetLife Stadium.",
    },
]


class TestApplyFixture:
    def test_agrega_eventos_nuevos(self, tmp_path):
        events_file = _write_events(tmp_path, [])
        added, replaced, total = apply_fixture(events_file, FIXTURE)
        assert (added, replaced, total) == (2, 0, 2)
        assert len(_read_events(events_file)) == 2

    def test_reemplaza_por_fecha_y_tipo(self, tmp_path):
        stale = {
            "date": "2026-07-03",
            "type": "match",
            "priority": "medium",
            "person": "N/A",
            "description": "Mundial 2026 - Día de descanso (desactualizado).",
        }
        events_file = _write_events(tmp_path, [stale])
        added, replaced, total = apply_fixture(events_file, FIXTURE)
        assert (added, replaced, total) == (1, 1, 2)

        events = _read_events(events_file)
        jul3 = [e for e in events if e["date"] == "2026-07-03"]
        assert len(jul3) == 1  # sin duplicados
        assert "Cabo Verde" in jul3[0]["description"]
        assert jul3[0]["priority"] == "critical"

    def test_idempotente(self, tmp_path):
        events_file = _write_events(tmp_path, [])
        apply_fixture(events_file, FIXTURE)
        first = _read_events(events_file)
        added, replaced, total = apply_fixture(events_file, FIXTURE)
        assert added == 0
        assert replaced == len(FIXTURE)
        assert total == len(FIXTURE)
        assert _read_events(events_file) == first

    def test_no_toca_eventos_de_otro_tipo_ni_fecha(self, tmp_path):
        birthday = {
            "date": "2026-07-03",
            "type": "birthday",
            "priority": "low",
            "person": "Alguien",
            "description": "Cumpleaños en fecha de partido.",
        }
        historical = {
            "date": "1986-06-22",
            "type": "match",
            "priority": "high",
            "person": "Diego Maradona",
            "description": "La mano de Dios y el Gol del Siglo.",
        }
        events_file = _write_events(tmp_path, [birthday, historical])
        added, replaced, total = apply_fixture(events_file, FIXTURE)
        assert (added, replaced, total) == (2, 0, 4)

        events = _read_events(events_file)
        assert birthday in events
        assert historical in events

    def test_ordena_por_fecha(self, tmp_path):
        historical = {
            "date": "1986-06-22",
            "type": "match",
            "priority": "high",
            "person": "N/A",
            "description": "México 86.",
        }
        events_file = _write_events(tmp_path, [historical])
        apply_fixture(events_file, FIXTURE)
        dates = [e["date"] for e in _read_events(events_file)]
        assert dates == sorted(dates)

    def test_usa_mundial_events_por_defecto(self, tmp_path):
        events_file = _write_events(tmp_path, [])
        added, replaced, total = apply_fixture(events_file)
        assert added == len(amf.MUNDIAL_EVENTS)
        assert replaced == 0
        assert total == len(amf.MUNDIAL_EVENTS)
