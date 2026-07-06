"""Tests for scripts/report_schema.py — validación aditiva de reports."""

import json
import sys
from importlib import import_module
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from report_schema import validate_report  # noqa: E402

REPORTS_DIR = ROOT / "reports"


def make_minimal_report():
    return {
        "date": "2026-06-15",
        "generated_at": "2026-06-15T08:00:00-03:00",
        "data": {"events": [], "news": []},
        "message": "Buenos días 🇦🇷\n\nBuen día\nCoronados de gloria vivamos 🩵🤍🩵",
        "status": "pending",
        "pre_approved": False,
    }


def make_claude_agent_report():
    report = make_minimal_report()
    report["source"] = "claude-agent"
    report["data"]["weather"] = {
        "amba": {"min": 8, "max": 16},
        "la_plata": {"min": 6, "max": 15},
    }
    report["data"]["sources"] = [
        "https://www.fifa.com/mundial2026",
        "http://example.com/noticia",
    ]
    report["data"]["mundial_2026_start"] = "2026-06-11"
    report["data"]["mundial_2026_end"] = "2026-07-19"
    return report


class TestMinimalReport:
    def test_valid_minimal_report_no_errors(self):
        report = make_minimal_report()
        assert validate_report(report) == []

    def test_missing_date_is_error(self):
        report = make_minimal_report()
        del report["date"]
        errors = validate_report(report)
        assert errors

    def test_malformed_date_is_error(self):
        report = make_minimal_report()
        report["date"] = "15-06-2026"
        errors = validate_report(report)
        assert errors

    def test_missing_generated_at_is_error(self):
        report = make_minimal_report()
        del report["generated_at"]
        errors = validate_report(report)
        assert errors

    def test_unparseable_generated_at_is_error(self):
        report = make_minimal_report()
        report["generated_at"] = "no es una fecha"
        errors = validate_report(report)
        assert errors

    def test_missing_data_is_error(self):
        report = make_minimal_report()
        del report["data"]
        errors = validate_report(report)
        assert errors

    def test_data_events_not_list_is_error(self):
        report = make_minimal_report()
        report["data"]["events"] = "no es lista"
        errors = validate_report(report)
        assert errors

    def test_data_news_not_list_is_error(self):
        report = make_minimal_report()
        report["data"]["news"] = "no es lista"
        errors = validate_report(report)
        assert errors

    def test_empty_message_is_error(self):
        report = make_minimal_report()
        report["message"] = ""
        errors = validate_report(report)
        assert errors

    def test_missing_message_is_error(self):
        report = make_minimal_report()
        del report["message"]
        errors = validate_report(report)
        assert errors

    def test_missing_status_is_error(self):
        report = make_minimal_report()
        del report["status"]
        errors = validate_report(report)
        assert errors

    def test_missing_pre_approved_is_error(self):
        report = make_minimal_report()
        del report["pre_approved"]
        errors = validate_report(report)
        assert errors

    def test_pre_approved_not_bool_is_error(self):
        report = make_minimal_report()
        report["pre_approved"] = "true"
        errors = validate_report(report)
        assert errors


class TestClaudeAgentReport:
    def test_complete_claude_agent_report_no_errors(self):
        report = make_claude_agent_report()
        assert validate_report(report) == []

    def test_weather_explicit_none_is_valid(self):
        report = make_claude_agent_report()
        report["data"]["weather"] = None
        assert validate_report(report) == []

    def test_missing_weather_key_is_error(self):
        report = make_claude_agent_report()
        del report["data"]["weather"]
        errors = validate_report(report)
        assert errors

    def test_missing_sources_is_error(self):
        report = make_claude_agent_report()
        del report["data"]["sources"]
        errors = validate_report(report)
        assert errors

    def test_empty_sources_list_is_error(self):
        report = make_claude_agent_report()
        report["data"]["sources"] = []
        errors = validate_report(report)
        assert errors

    def test_sources_not_http_is_error(self):
        report = make_claude_agent_report()
        report["data"]["sources"] = ["ftp://example.com/file"]
        errors = validate_report(report)
        assert errors

    def test_sources_not_list_of_strings_is_error(self):
        report = make_claude_agent_report()
        report["data"]["sources"] = [{"url": "https://example.com"}]
        errors = validate_report(report)
        assert errors

    def test_missing_mundial_2026_start_is_error(self):
        report = make_claude_agent_report()
        del report["data"]["mundial_2026_start"]
        errors = validate_report(report)
        assert errors

    def test_malformed_mundial_2026_start_is_error(self):
        report = make_claude_agent_report()
        report["data"]["mundial_2026_start"] = "11-06-2026"
        errors = validate_report(report)
        assert errors

    def test_mundial_2026_start_present_is_valid(self):
        report = make_claude_agent_report()
        assert validate_report(report) == []

    def test_generated_at_naive_is_error(self):
        report = make_claude_agent_report()
        report["generated_at"] = "2026-06-15T08:00:00"
        errors = validate_report(report)
        assert errors

    def test_generated_at_with_z_offset_is_valid(self):
        report = make_claude_agent_report()
        report["generated_at"] = "2026-06-15T11:00:00Z"
        assert validate_report(report) == []

    def test_malformed_date_is_error(self):
        report = make_claude_agent_report()
        report["date"] = "2026/06/15"
        errors = validate_report(report)
        assert errors

    def test_empty_message_is_error(self):
        report = make_claude_agent_report()
        report["message"] = ""
        errors = validate_report(report)
        assert errors


class TestOldReportsCompat:
    """Un report real viejo del repo (sin source, formatos previos) no debe
    romper con la validación aditiva."""

    def test_real_old_report_no_errors(self):
        report_path = REPORTS_DIR / "2026-06-27.json"
        assert report_path.exists(), f"fixture {report_path} no existe"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        errors = validate_report(report)
        assert errors == [], f"errores inesperados en report viejo: {errors}"


class TestCLI:
    def test_cli_valid_report_exit_0(self, tmp_path, monkeypatch, capsys):
        report_schema = import_module("report_schema")

        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        report = make_minimal_report()
        (reports_dir / "2026-06-15.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )

        monkeypatch.setattr(report_schema, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(sys, "argv", ["report_schema.py", "--date", "2026-06-15"])

        with pytest.raises(SystemExit) as exc_info:
            report_schema.main()
        assert exc_info.value.code == 0

    def test_cli_invalid_report_exit_1(self, tmp_path, monkeypatch, capsys):
        report_schema = import_module("report_schema")

        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        report = make_minimal_report()
        del report["message"]
        (reports_dir / "2026-06-15.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )

        monkeypatch.setattr(report_schema, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(sys, "argv", ["report_schema.py", "--date", "2026-06-15"])

        with pytest.raises(SystemExit) as exc_info:
            report_schema.main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert captured.out or captured.err
