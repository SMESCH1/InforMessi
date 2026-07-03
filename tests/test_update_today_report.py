"""Tests for scripts/update-today-report.py — detección del report del
agente Claude (source == "claude-agent") antes de regenerar con Groq."""

import json
import sys
from importlib import import_module
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from time_utils import now_ar_iso, today_ar  # noqa: E402

utr = import_module("update-today-report")


def make_agent_report(date: str, generated_at: str, message: str = "mensaje del agente"):
    return {
        "date": date,
        "generated_at": generated_at,
        "source": "claude-agent",
        "data": {
            "events": [],
            "news": [],
            "weather": {"amba": {"min": 8, "max": 16}, "la_plata": {"min": 6, "max": 15}},
            "sources": ["https://www.fifa.com/mundial2026"],
        },
        "message": message,
        "status": "agent-draft",
        "pre_approved": False,
    }


class TestAgentReportDetection:
    def test_fresh_valid_agent_report_short_circuits_groq(self, tmp_path, monkeypatch):
        """Report fresco (generated_at de hoy, válido) del agente: se debe
        aceptar sin invocar subprocess (Groq) en absoluto."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        today = today_ar()
        report = make_agent_report(today, now_ar_iso())
        report_path = reports_dir / f"{today}.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(utr, "REPORTS_DIR", reports_dir)

        calls = []

        def fake_run(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("subprocess.run no debería invocarse para un report fresco del agente")

        monkeypatch.setattr(utr.subprocess, "run", fake_run)

        result = utr.update_report_for_date(today)

        assert result is True
        assert calls == []

        saved = json.loads(report_path.read_text(encoding="utf-8"))
        assert saved["source"] == "claude-agent"
        assert "updated_at" in saved
        # pre_approved no debe tocarse: el flujo de aprobación manual sigue igual
        assert saved["pre_approved"] is False

    def test_stale_agent_report_falls_back_to_groq(self, tmp_path, monkeypatch):
        """generated_at de un día distinto a `date`: se considera stale y
        debe seguir el path de regeneración Groq (subprocess.run se invoca)."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        today = today_ar()
        stale_generated_at = "2020-01-01T08:00:00-03:00"
        report = make_agent_report(today, stale_generated_at)
        report_path = reports_dir / f"{today}.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(utr, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(utr, "PROJECT_ROOT", tmp_path)

        calls = []

        class FakeCompletedProcess:
            def __init__(self):
                self.returncode = 1
                self.stdout = ""
                self.stderr = "boom"

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return FakeCompletedProcess()

        monkeypatch.setattr(utr.subprocess, "run", fake_run)

        result = utr.update_report_for_date(today)

        assert len(calls) >= 1, "subprocess.run debería haberse invocado (path Groq)"
        assert result is False  # collect-daily-data.py "falló" (mock), así que update falla

    def test_invalid_agent_report_falls_back_to_groq(self, tmp_path, monkeypatch):
        """Report con source=claude-agent, generated_at de hoy, pero que no
        pasa validate_report (falta data.sources): debe caer al path Groq."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        today = today_ar()
        report = make_agent_report(today, now_ar_iso())
        del report["data"]["sources"]  # invalida el report para un claude-agent
        report_path = reports_dir / f"{today}.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(utr, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(utr, "PROJECT_ROOT", tmp_path)

        calls = []

        class FakeCompletedProcess:
            def __init__(self):
                self.returncode = 1
                self.stdout = ""
                self.stderr = "boom"

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return FakeCompletedProcess()

        monkeypatch.setattr(utr.subprocess, "run", fake_run)

        result = utr.update_report_for_date(today)

        assert len(calls) >= 1, "subprocess.run debería haberse invocado (path Groq) por report inválido"
        assert result is False

    def test_agent_report_without_message_falls_back_to_groq(self, tmp_path, monkeypatch):
        """generated_at de hoy pero sin message (falsy): no debe tomarse el
        atajo del agente."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        today = today_ar()
        report = make_agent_report(today, now_ar_iso(), message="")
        report_path = reports_dir / f"{today}.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(utr, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(utr, "PROJECT_ROOT", tmp_path)

        calls = []

        class FakeCompletedProcess:
            def __init__(self):
                self.returncode = 1
                self.stdout = ""
                self.stderr = "boom"

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return FakeCompletedProcess()

        monkeypatch.setattr(utr.subprocess, "run", fake_run)

        result = utr.update_report_for_date(today)

        assert len(calls) >= 1
        assert result is False


    def test_agent_report_with_malformed_generated_at_falls_back_to_groq(self, tmp_path, monkeypatch):
        """generated_at corrupto/no parseable no debe tirar una excepción:
        debe tratarse como stale y caer al path Groq."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        today = today_ar()
        report = make_agent_report(today, now_ar_iso())
        report["generated_at"] = "esto no es una fecha"
        report_path = reports_dir / f"{today}.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(utr, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(utr, "PROJECT_ROOT", tmp_path)

        calls = []

        class FakeCompletedProcess:
            def __init__(self):
                self.returncode = 1
                self.stdout = ""
                self.stderr = "boom"

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return FakeCompletedProcess()

        monkeypatch.setattr(utr.subprocess, "run", fake_run)

        result = utr.update_report_for_date(today)

        assert len(calls) >= 1
        assert result is False


class TestGroqFallbackSetsSource:
    def test_regeneration_path_sets_source_groq_fallback(self, tmp_path, monkeypatch):
        """Cuando el flujo Groq efectivamente regenera el report (no-agent
        report, con cambios), el report guardado debe llevar
        source == 'groq-fallback'."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        tmp_dir = tmp_path / "tmp"

        today = today_ar()
        report = {
            "date": today,
            "generated_at": "2020-01-01T08:00:00-03:00",
            "data": {"events": [], "news": [{"title": "vieja"}]},
            "message": "mensaje viejo",
            "status": "pending",
            "pre_approved": False,
        }
        report_path = reports_dir / f"{today}.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(utr, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(utr, "PROJECT_ROOT", tmp_path)

        updated_data = {"events": [], "news": [{"title": "nueva noticia"}]}
        new_message = "mensaje nuevo generado por groq"

        class FakeCompletedProcess:
            def __init__(self, returncode=0):
                self.returncode = returncode
                self.stdout = ""
                self.stderr = ""

        def fake_run(cmd, **kwargs):
            # cmd[1] es el script invocado (collect-daily-data.py o generate-message.py)
            script = str(cmd[1])
            if "collect-daily-data.py" in script:
                data_file = tmp_dir / f"data-{today}.json"
                data_file.parent.mkdir(parents=True, exist_ok=True)
                data_file.write_text(json.dumps(updated_data, ensure_ascii=False), encoding="utf-8")
            elif "generate-message.py" in script:
                message_file = tmp_dir / f"message-{today}.txt"
                message_file.parent.mkdir(parents=True, exist_ok=True)
                message_file.write_text(new_message, encoding="utf-8")
            return FakeCompletedProcess(returncode=0)

        monkeypatch.setattr(utr.subprocess, "run", fake_run)

        result = utr.update_report_for_date(today)

        assert result is True
        saved = json.loads(report_path.read_text(encoding="utf-8"))
        assert saved["source"] == "groq-fallback"
        assert saved["message"] == new_message
