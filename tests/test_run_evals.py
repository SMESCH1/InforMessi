"""Tests for evals/judge.py y evals/run_evals.py — judge LLM y orquestador de evals."""

import json
import sys
from importlib import import_module
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from evals import judge as judge_mod
from evals.judge import judge_message

run_evals = import_module("evals.run_evals")

REPORTS_DIR = ROOT / "reports"


# --- Fixtures compartidas ---

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
        "source": "claude-agent",
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


# --- judge_message ---

class TestJudgeMessage:
    def test_valid_json_returns_dict_with_promedio(self, monkeypatch):
        def fake_call_groq(prompt, model=None, temperature=None, max_tokens=None,
                            json_mode=None, system=None):
            return json.dumps({
                "tono": 5, "estructura": 5, "fidelidad_guia": 4,
                "factualidad_aparente": 5, "comentario": "Buen mensaje."
            })

        monkeypatch.setattr(judge_mod, "call_groq", fake_call_groq)

        result = judge_message("mensaje de prueba", {"events": [], "news": [], "weather": {}})

        assert result is not None
        assert result["tono"] == 5
        assert result["estructura"] == 5
        assert result["fidelidad_guia"] == 4
        assert result["factualidad_aparente"] == 5
        assert result["promedio"] == pytest.approx(4.75, abs=0.01)
        assert "model" in result

    def test_invalid_json_returns_none(self, monkeypatch):
        def fake_call_groq(prompt, model=None, temperature=None, max_tokens=None,
                            json_mode=None, system=None):
            return "esto no es json ni se le parece"

        monkeypatch.setattr(judge_mod, "call_groq", fake_call_groq)

        result = judge_message("mensaje de prueba", {"events": [], "news": [], "weather": {}})
        assert result is None

    def test_missing_dimension_returns_none(self, monkeypatch):
        def fake_call_groq(prompt, model=None, temperature=None, max_tokens=None,
                            json_mode=None, system=None):
            return json.dumps({"tono": 5, "estructura": 5, "comentario": "falta fidelidad y factualidad"})

        monkeypatch.setattr(judge_mod, "call_groq", fake_call_groq)

        result = judge_message("mensaje de prueba", {"events": [], "news": [], "weather": {}})
        assert result is None

    def test_out_of_range_score_returns_none(self, monkeypatch):
        def fake_call_groq(prompt, model=None, temperature=None, max_tokens=None,
                            json_mode=None, system=None):
            return json.dumps({
                "tono": 9, "estructura": 5, "fidelidad_guia": 4,
                "factualidad_aparente": 5, "comentario": "score inválido"
            })

        monkeypatch.setattr(judge_mod, "call_groq", fake_call_groq)

        result = judge_message("mensaje de prueba", {"events": [], "news": [], "weather": {}})
        assert result is None

    def test_api_error_returns_none(self, monkeypatch):
        def fake_call_groq(prompt, model=None, temperature=None, max_tokens=None,
                            json_mode=None, system=None):
            raise RuntimeError("Groq caído")

        monkeypatch.setattr(judge_mod, "call_groq", fake_call_groq)

        result = judge_message("mensaje de prueba", {"events": [], "news": [], "weather": {}})
        assert result is None

    def test_missing_groq_api_key_returns_none_without_crashing(self, monkeypatch):
        """CRITICAL: judge_message no debe tirar el proceso abajo si falta
        GROQ_API_KEY. Ejercita el path real de scripts/llm_client.call_groq
        (sin mockear call_groq) para probar que LLMClientError -- no
        SystemExit -- es lo que se propaga y es capturado por el except
        Exception de judge_message."""
        monkeypatch.delenv("GROQ_API_KEY", raising=False)

        result = judge_message("mensaje de prueba", {"events": [], "news": [], "weather": {}})

        assert result is None

    def test_model_param_propagates(self, monkeypatch):
        captured = {}

        def fake_call_groq(prompt, model=None, temperature=None, max_tokens=None,
                            json_mode=None, system=None):
            captured["model"] = model
            captured["temperature"] = temperature
            captured["max_tokens"] = max_tokens
            captured["json_mode"] = json_mode
            captured["system"] = system
            return json.dumps({
                "tono": 3, "estructura": 3, "fidelidad_guia": 3,
                "factualidad_aparente": 3, "comentario": "ok"
            })

        monkeypatch.setattr(judge_mod, "call_groq", fake_call_groq)

        result = judge_message("mensaje", {"events": []}, model="custom-model")

        assert captured["model"] == "custom-model"
        assert captured["temperature"] == 0
        assert captured["max_tokens"] == 400
        assert captured["json_mode"] is True
        assert captured["system"] is not None
        assert result["model"] == "custom-model"


# --- verdict logic (run_evals) ---

class TestComputeVerdict:
    def test_pass_when_checks_pass_and_no_judge(self):
        report = make_good_report()
        checks = run_evals.run_checks(report)
        verdict = run_evals.compute_verdict(checks, judge=None)
        assert verdict == "pass"

    def test_fail_when_error_check_fails(self):
        report = make_good_report()
        report["message"] = "mensaje roto sin saludo ni estructura"
        checks = run_evals.run_checks(report)
        verdict = run_evals.compute_verdict(checks, judge=None)
        assert verdict == "fail"

    def test_pass_with_warnings_when_only_warning_fails(self):
        report = make_good_report()
        # Sacar emojis "extra" (no el saludo 🇦🇷 ni el cierre 🩵🤍🩵, que son
        # obligatorios para los checks de error) para forzar solo el warning
        # de "emojis" sin tocar ningún check de severity=error.
        report["message"] = report["message"].replace("🌤 ", "").replace("🏆 ", "").replace(" 🩵🤍🩵", "")
        checks = run_evals.run_checks(report)
        summary = run_evals.summarize(checks)
        assert summary["errors_failed"] == 0, f"no debería haber errors_failed: {checks}"
        assert summary["warnings_failed"] > 0, "se esperaba al menos un warning fallado (emojis)"
        verdict = run_evals.compute_verdict(checks, judge=None)
        assert verdict == "pass_with_warnings"

    def test_fail_when_judge_promedio_low_even_if_checks_pass(self):
        report = make_good_report()
        checks = run_evals.run_checks(report)
        judge_result = {
            "tono": 2, "estructura": 3, "fidelidad_guia": 2,
            "factualidad_aparente": 3, "promedio": 2.5, "comentario": "flojo", "model": "m"
        }
        verdict = run_evals.compute_verdict(checks, judge=judge_result)
        assert verdict == "fail"

    def test_pass_when_judge_promedio_high_and_checks_pass(self):
        report = make_good_report()
        checks = run_evals.run_checks(report)
        judge_result = {
            "tono": 5, "estructura": 5, "fidelidad_guia": 5,
            "factualidad_aparente": 5, "promedio": 5.0, "comentario": "excelente", "model": "m"
        }
        verdict = run_evals.compute_verdict(checks, judge=judge_result)
        assert verdict == "pass"


# --- eval-history ---

class TestEvalHistory:
    def test_run_evals_appends_history_entry(self, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        exit_code = run_evals.run_for_date("2026-06-15", gate=False, use_judge=False, on_fail=None)

        assert exit_code == 0

        history_path = data_dir / "eval-history.json"
        assert history_path.exists()
        history = json.loads(history_path.read_text(encoding="utf-8"))
        assert isinstance(history, list)
        assert len(history) == 1
        entry = history[0]
        assert entry["date"] == "2026-06-15"
        assert entry["source"] == "claude-agent"
        assert entry["verdict"] == "pass"
        assert "run_at" in entry
        assert entry["judge_scores"] is None
        assert entry["model"] is None

        # El report también debe llevar el bloque eval
        updated_report = json.loads(report_path.read_text(encoding="utf-8"))
        assert "eval" in updated_report
        assert updated_report["eval"]["verdict"] == "pass"

    def test_run_evals_appends_to_existing_history_list(self, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        history_path = data_dir / "eval-history.json"
        history_path.write_text(json.dumps([{"date": "2026-06-14", "verdict": "pass"}]), encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", history_path)

        run_evals.run_for_date("2026-06-15", gate=False, use_judge=False, on_fail=None)

        history = json.loads(history_path.read_text(encoding="utf-8"))
        assert len(history) == 2
        assert history[0]["date"] == "2026-06-14"
        assert history[1]["date"] == "2026-06-15"

    def test_exit_code_1_on_fail_when_gate(self, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report["message"] = "mensaje totalmente roto"
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        exit_code = run_evals.run_for_date("2026-06-15", gate=True, use_judge=False, on_fail=None)
        assert exit_code == 1

    def test_exit_code_1_on_fail_without_gate(self, tmp_path, monkeypatch):
        """Según el plan: sin --on-fail, exit 1 en fail es independiente de
        --gate (--gate es redundante/no-op, el gate es el default)."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report["message"] = "mensaje totalmente roto"
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        exit_code = run_evals.run_for_date("2026-06-15", gate=False, use_judge=False, on_fail=None)
        assert exit_code == 1

    def test_eval_warning_set_on_fail_without_on_fail_flag(self, tmp_path, monkeypatch):
        """Cualquier camino donde el veredicto FINAL sea fail (con o sin
        --on-fail) debe dejar eval_warning=True y pre_approved=False en el
        report guardado: un report con evals fallidas jamás se auto-publica."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report["message"] = "mensaje totalmente roto"
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        exit_code = run_evals.run_for_date("2026-06-15", gate=False, use_judge=False, on_fail=None)

        assert exit_code == 1
        updated_report = json.loads(report_path.read_text(encoding="utf-8"))
        assert updated_report.get("eval_warning") is True
        assert updated_report.get("pre_approved") is False


# --- --on-fail regenerate ---

class TestOnFailRegenerate:
    def test_regenerate_invoked_when_verdict_fail(self, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report["message"] = "mensaje totalmente roto sin estructura"
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        calls = []

        def fake_regenerate(report_arg, date):
            calls.append((report_arg.get("date"), date))
            # simular que la regeneración no arregla nada (sigue mal) para no
            # depender de un segundo ciclo de checks distinto
            return report_arg["message"]

        monkeypatch.setattr(run_evals, "_regenerate_message", fake_regenerate)

        exit_code = run_evals.run_for_date("2026-06-15", gate=True, use_judge=False, on_fail="regenerate")

        assert len(calls) == 1
        assert calls[0][1] == "2026-06-15"
        assert exit_code == 0  # on-fail siempre exit 0 según spec

        updated_report = json.loads(report_path.read_text(encoding="utf-8"))
        assert updated_report.get("eval_warning") is True
        assert updated_report.get("pre_approved") is False

    def test_regenerate_not_invoked_when_verdict_pass(self, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        calls = []
        monkeypatch.setattr(run_evals, "_regenerate_message", lambda report_arg, date: calls.append(date))

        exit_code = run_evals.run_for_date("2026-06-15", gate=True, use_judge=False, on_fail="regenerate")

        assert calls == []
        assert exit_code == 0

    def test_regenerate_success_clears_eval_warning(self, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report["message"] = "mensaje totalmente roto"
        report["eval_warning"] = True
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        # La regeneración "arregla" el mensaje devolviendo el bueno
        monkeypatch.setattr(run_evals, "_regenerate_message", lambda report_arg, date: GOOD_MESSAGE)

        exit_code = run_evals.run_for_date("2026-06-15", gate=True, use_judge=False, on_fail="regenerate")

        assert exit_code == 0
        updated_report = json.loads(report_path.read_text(encoding="utf-8"))
        assert updated_report.get("eval_warning") is not True
        assert updated_report["eval"]["verdict"] == "pass"


# --- --range ---

class TestRangeMode:
    def test_range_iterates_and_skips_missing(self, tmp_path, monkeypatch, capsys):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report["date"] = "2026-06-15"
        report["data"]["date"] = "2026-06-15"
        (reports_dir / "2026-06-15.json").write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        # 2026-06-16 falta a propósito

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        exit_code = run_evals.run_range("2026-06-15", "2026-06-16", gate=False, use_judge=False)

        assert exit_code == 0
        history = json.loads((data_dir / "eval-history.json").read_text(encoding="utf-8"))
        assert len(history) == 1
        assert history[0]["date"] == "2026-06-15"

    def test_range_exit_0_even_with_fail_verdict(self, tmp_path, monkeypatch):
        """--range siempre exit 0, incluso si algún report del rango falla
        los checks (es para backfill/baseline, no debe romper CI)."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report["message"] = "mensaje totalmente roto"
        report["date"] = "2026-06-15"
        report["data"]["date"] = "2026-06-15"
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        exit_code = run_evals.run_range("2026-06-15", "2026-06-15", gate=False, use_judge=False)

        assert exit_code == 0
        updated_report = json.loads(report_path.read_text(encoding="utf-8"))
        assert updated_report["eval"]["verdict"] == "fail"
        # eval_warning también debe quedar seteado dentro de un --range
        assert updated_report.get("eval_warning") is True


# --- exit codes de los 3 modos (spec del plan) ---

class TestExitCodeSemantics:
    def _write_failing_report(self, reports_dir, date="2026-06-15"):
        report = make_good_report()
        report["message"] = "mensaje totalmente roto"
        report["date"] = date
        report["data"]["date"] = date
        (reports_dir / f"{date}.json").write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

    def test_no_on_fail_exit_1_on_fail_regardless_of_gate(self, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        self._write_failing_report(reports_dir)

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        # Sin --gate
        assert run_evals.run_for_date("2026-06-15", gate=False, use_judge=False, on_fail=None) == 1
        # Con --gate (debe dar el mismo resultado: --gate es no-op)
        assert run_evals.run_for_date("2026-06-15", gate=True, use_judge=False, on_fail=None) == 1

    def test_on_fail_regenerate_exit_0_always(self, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        self._write_failing_report(reports_dir)

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")
        monkeypatch.setattr(run_evals, "_regenerate_message", lambda report_arg, date: report_arg["message"])

        for gate in (False, True):
            exit_code = run_evals.run_for_date("2026-06-15", gate=gate, use_judge=False, on_fail="regenerate")
            assert exit_code == 0

    def test_range_mode_exit_0_always(self, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        self._write_failing_report(reports_dir)

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", data_dir / "eval-history.json")

        for gate in (False, True):
            exit_code = run_evals.run_range("2026-06-15", "2026-06-15", gate=gate, use_judge=False)
            assert exit_code == 0


# --- historial corrupto ---

class TestCorruptHistoryBackup:
    def test_invalid_json_backed_up_before_overwrite(self, tmp_path, monkeypatch, caplog):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        history_path = data_dir / "eval-history.json"
        history_path.write_text("{ esto no es json valido", encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", history_path)

        with caplog.at_level("WARNING"):
            run_evals.run_for_date("2026-06-15", gate=False, use_judge=False, on_fail=None)

        backup_path = data_dir / "eval-history.json.bak"
        assert backup_path.exists()
        assert backup_path.read_text(encoding="utf-8") == "{ esto no es json valido"

        # El archivo nuevo debe ser una lista JSON válida con la entry nueva
        new_history = json.loads(history_path.read_text(encoding="utf-8"))
        assert isinstance(new_history, list)
        assert len(new_history) == 1
        assert new_history[0]["date"] == "2026-06-15"

        assert any("inválido" in rec.message or "invalido" in rec.message for rec in caplog.records)

    def test_non_list_json_backed_up_before_overwrite(self, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        report = make_good_report()
        report_path = reports_dir / "2026-06-15.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        history_path = data_dir / "eval-history.json"
        history_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

        monkeypatch.setattr(run_evals, "REPORTS_DIR", reports_dir)
        monkeypatch.setattr(run_evals, "DATA_DIR", data_dir)
        monkeypatch.setattr(run_evals, "EVAL_HISTORY_PATH", history_path)

        run_evals.run_for_date("2026-06-15", gate=False, use_judge=False, on_fail=None)

        backup_path = data_dir / "eval-history.json.bak"
        assert backup_path.exists()
        backed_up = json.loads(backup_path.read_text(encoding="utf-8"))
        assert backed_up == {"not": "a list"}

        new_history = json.loads(history_path.read_text(encoding="utf-8"))
        assert isinstance(new_history, list)
        assert len(new_history) == 1


# --- integración: should_auto_publish con eval_warning ---

class TestAutoPublishEvalWarning:
    def test_should_auto_publish_false_when_eval_warning(self):
        apf = import_module("auto-publish-fallback")
        report = {
            "eval_warning": True,
            "status": "pending",
            "updated_at": "2020-01-01T00:00:00-03:00",
        }
        assert apf.should_auto_publish(report, hours_threshold=0) is False

    def test_should_auto_publish_normal_path_unaffected(self):
        apf = import_module("auto-publish-fallback")
        from time_utils import now_ar_iso
        report = {
            "status": "pending",
            "updated_at": now_ar_iso(),
        }
        # hours_threshold alto, todavia no debe publicar por tiempo, pero no por eval_warning
        assert apf.should_auto_publish(report, hours_threshold=999) is False
