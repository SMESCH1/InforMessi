"""Tests for rag_memory_database.py core functions."""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from importlib import import_module

rmd = import_module("rag_memory_database")

MemoryDatabase = rmd.MemoryDatabase
_normalize_text = rmd._normalize_text


class TestNormalizeText:
    def test_lowercase(self):
        assert _normalize_text("HELLO") == "hello"

    def test_strip_accents(self):
        assert _normalize_text("Selección") == "seleccion"
        assert _normalize_text("fútbol") == "futbol"
        assert _normalize_text("año") == "ano"

    def test_collapse_whitespace(self):
        assert _normalize_text("  hello   world  ") == "hello world"

    def test_combined(self):
        assert _normalize_text("  La Selección Argentina  ") == "la seleccion argentina"


class TestMemoryDatabase:
    def _make_db(self, tmp_path):
        db = MemoryDatabase.__new__(MemoryDatabase)
        db.db_file = Path(tmp_path) / "test-memory.json"
        db.data = db._create_empty_database()
        return db

    def test_record_player(self, tmp_path):
        db = self._make_db(tmp_path)
        db.record_player_used("Messi", "2026-02-01")
        assert "Messi" in db.data["players_used"]
        assert "2026-02-01" in db.data["players_used"]["Messi"]

    def test_no_duplicate_dates(self, tmp_path):
        db = self._make_db(tmp_path)
        db.record_player_used("Messi", "2026-02-01")
        db.record_player_used("Messi", "2026-02-01")
        assert len(db.data["players_used"]["Messi"]) == 1

    def test_record_news_normalized(self, tmp_path):
        db = self._make_db(tmp_path)
        db.record_news("Selección Argentina clasifica al Mundial", "2026-02-01")
        keys = list(db.data["news_topics"].keys())
        assert len(keys) == 1
        assert "seleccion" in keys[0]

    def test_record_news_truncated(self, tmp_path):
        db = self._make_db(tmp_path)
        long_title = "A" * 200
        db.record_news(long_title, "2026-02-01")
        keys = list(db.data["news_topics"].keys())
        assert len(keys[0]) == 50

    def test_record_fact(self, tmp_path):
        db = self._make_db(tmp_path)
        db.record_fact("El Mundial 2026 tendrá 48 equipos", "2026-02-01")
        assert "El Mundial 2026 tendrá 48 equipos" in db.data["facts_used"]

    def test_record_weekly_section(self, tmp_path):
        db = self._make_db(tmp_path)
        db.record_weekly_section("seleccion_mundiales", "2026-02-02")
        assert "2026-02-02" in db.data["weekly_sections"]["seleccion_mundiales"]

    def test_analyze_report_extracts_players(self, tmp_path):
        db = self._make_db(tmp_path)
        report = {
            "date": "2026-02-02",  # Monday
            "message": "Messi lideró al equipo con Di María apoyando",
            "data": {"events": [], "news": []},
        }
        db.analyze_report(report)
        assert "Messi" in db.data["players_used"]
        assert "Di María" in db.data["players_used"]

    def test_analyze_report_extracts_fact(self, tmp_path):
        db = self._make_db(tmp_path)
        report = {
            "date": "2026-02-03",
            "message": "Hola\n📊 Dato del día: Argentina ganó 3 mundiales\nChau",
            "data": {"events": [], "news": []},
        }
        db.analyze_report(report)
        assert len(db.data["facts_used"]) == 1
        fact_key = list(db.data["facts_used"].keys())[0]
        assert "Argentina" in fact_key

    def test_analyze_report_matches_news_partial(self, tmp_path):
        db = self._make_db(tmp_path)
        report = {
            "date": "2026-02-03",
            "message": "messi anoto un gol en el partido de ayer contra brasil en un amistoso importante",
            "data": {
                "events": [],
                "news": [
                    {"title": "Messi anotó un gol en el partido de ayer"},
                    {"title": "Noticias completamente diferentes no relacionadas"},
                ],
            },
        }
        db.analyze_report(report)
        assert len(db.data["news_topics"]) == 1

    def test_get_least_used_players(self, tmp_path):
        db = self._make_db(tmp_path)
        db.record_player_used("Messi", "2026-01-01")
        db.record_player_used("Messi", "2026-01-02")
        db.record_player_used("Di María", "2026-01-01")

        players = [{"name": "Messi"}, {"name": "Di María"}, {"name": "Lautaro"}]
        result = db.get_least_used_players(players, limit=2)
        assert result[0]["name"] == "Lautaro"
        assert result[1]["name"] == "Di María"
