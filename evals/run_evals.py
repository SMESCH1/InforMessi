#!/usr/bin/env python3
"""Orquestador CLI de evals para InforMessi.

python evals/run_evals.py --date YYYY-MM-DD [--range A:B] [--gate] [--judge] [--on-fail regenerate]

Corre los checks programáticos (evals/checks.py) y, opcionalmente, el judge
LLM (evals/judge.py) sobre un report. Escribe el resultado en
report["eval"], appendea data/eval-history.json, y opcionalmente regenera
el mensaje si el veredicto es "fail".
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from evals.checks import run_checks, summarize  # noqa: E402
from evals.judge import judge_message  # noqa: E402
from time_utils import now_ar_iso, today_ar  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

REPORTS_DIR = ROOT / "reports"
DATA_DIR = ROOT / "data"
EVAL_HISTORY_PATH = DATA_DIR / "eval-history.json"

DEFAULT_JUDGE_MODEL = "llama-3.3-70b-versatile"


def compute_verdict(checks: list, judge: dict | None) -> str:
    """fail si algún check de error falló, o si hay judge con promedio < 3.0.
    pass_with_warnings si solo fallaron warnings. sino pass."""
    summary = summarize(checks)
    if summary["errors_failed"] > 0:
        return "fail"
    if judge is not None and judge.get("promedio", 5) < 3.0:
        return "fail"
    if summary["warnings_failed"] > 0:
        return "pass_with_warnings"
    return "pass"


def _load_report(date: str) -> dict | None:
    report_path = REPORTS_DIR / f"{date}.json"
    if not report_path.exists():
        return None
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_report(date: str, report: dict) -> None:
    report_path = REPORTS_DIR / f"{date}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def _append_history(entry: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if EVAL_HISTORY_PATH.exists():
        try:
            history = json.loads(EVAL_HISTORY_PATH.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = []
        except (json.JSONDecodeError, OSError):
            history = []
    else:
        history = []

    history.append(entry)

    with open(EVAL_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _run_checks_and_judge(report: dict, date: str, use_judge: bool):
    checks = run_checks(report, expected_date=date)
    judge_result = None
    if use_judge:
        judge_result = judge_message(report.get("message", ""), report.get("data", {}), model=DEFAULT_JUDGE_MODEL)
    verdict = compute_verdict(checks, judge_result)
    return checks, judge_result, verdict


def _write_eval_block(report: dict, checks: list, judge_result: dict | None, verdict: str) -> None:
    report["eval"] = {
        "run_at": now_ar_iso(),
        "checks": checks,
        "judge": judge_result,
        "verdict": verdict,
    }


def _regenerate_message(report: dict, date: str) -> str | None:
    """Regenera report["message"] llamando a scripts/generate-message.py con
    los datos ya presentes en report["data"], siguiendo el mismo patrón que
    scripts/update-today-report.py (escribir data a tmp/, invocar con
    --data/--output/--provider, leer el .txt resultante).

    Retorna el nuevo mensaje, o None si la regeneración falló.
    """
    import os

    tmp_dir = ROOT / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    data_file = tmp_dir / f"eval-regen-data-{date}.json"
    message_file = tmp_dir / f"eval-regen-message-{date}.txt"

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(report.get("data", {}), f, ensure_ascii=False)

    provider = os.environ.get("LLM_PROVIDER", "ollama")

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "generate-message.py"),
                "--data",
                str(data_file),
                "--output",
                str(message_file),
                "--provider",
                provider,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception as e:
        logger.warning(f"_regenerate_message: error al invocar generate-message.py: {e}")
        return None

    if result.returncode != 0:
        logger.warning(f"_regenerate_message: generate-message.py falló: {result.stderr}")
        return None

    try:
        return message_file.read_text(encoding="utf-8")
    except OSError as e:
        logger.warning(f"_regenerate_message: no se pudo leer el mensaje regenerado: {e}")
        return None


def run_for_date(date: str, gate: bool, use_judge: bool, on_fail: str | None) -> int:
    """Corre checks (+judge opcional) sobre el report de `date`, guarda el
    resultado, appendea a eval-history.json y retorna el exit code."""
    report = _load_report(date)
    if report is None:
        logger.warning(f"⚠️  Informe para {date} no encontrado, se omite.")
        return 0

    checks, judge_result, verdict = _run_checks_and_judge(report, date, use_judge)
    _write_eval_block(report, checks, judge_result, verdict)

    if verdict == "fail" and on_fail == "regenerate":
        new_message = _regenerate_message(report, date)
        if new_message:
            report["message"] = new_message
            checks, judge_result, verdict = _run_checks_and_judge(report, date, use_judge)
            _write_eval_block(report, checks, judge_result, verdict)

        if verdict == "fail":
            report["eval_warning"] = True
            report["pre_approved"] = False
        else:
            if report.get("eval_warning"):
                report.pop("eval_warning", None)

        _save_report(date, report)
        _append_history(_history_entry(date, report, checks, judge_result, verdict, use_judge))
        return 0

    _save_report(date, report)
    _append_history(_history_entry(date, report, checks, judge_result, verdict, use_judge))

    if on_fail is not None:
        return 0

    return 1 if (gate and verdict == "fail") else 0


def _history_entry(date, report, checks, judge_result, verdict, use_judge) -> dict:
    summary = summarize(checks)
    return {
        "date": date,
        "run_at": now_ar_iso(),
        "source": report.get("source", "unknown"),
        "model": (judge_result or {}).get("model") if use_judge and judge_result else None,
        "checks_passed": summary["passed"],
        "checks_failed": summary["errors_failed"],
        "warnings_failed": summary["warnings_failed"],
        "judge_scores": judge_result,
        "verdict": verdict,
    }


def _date_range(start: str, end: str):
    from datetime import date as date_cls, timedelta

    start_d = date_cls.fromisoformat(start)
    end_d = date_cls.fromisoformat(end)
    current = start_d
    while current <= end_d:
        yield current.isoformat()
        current += timedelta(days=1)


def run_range(start: str, end: str, gate: bool, use_judge: bool) -> int:
    """Itera fechas de start a end (inclusive), corre eval por cada report
    existente (sin --on-fail, es para backfill/baseline). Siempre exit 0."""
    for date in _date_range(start, end):
        report = _load_report(date)
        if report is None:
            logger.warning(f"⚠️  Informe para {date} no encontrado, se omite (range mode).")
            continue
        run_for_date(date, gate=gate, use_judge=use_judge, on_fail=None)
    return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Orquestador de evals para InforMessi")
    parser.add_argument("--date", help="Fecha a evaluar (YYYY-MM-DD). Default: hoy")
    parser.add_argument("--range", help="Rango de fechas A:B (ambos extremos inclusive), para backfill")
    parser.add_argument("--gate", action="store_true", help="Exit code 1 si el veredicto es fail")
    parser.add_argument("--judge", action="store_true", help="Correr también el judge LLM")
    parser.add_argument("--on-fail", choices=["regenerate"], help="Acción a tomar si el veredicto es fail")

    args = parser.parse_args()

    if args.range:
        start, end = args.range.split(":")
        exit_code = run_range(start, end, gate=args.gate, use_judge=args.judge)
        sys.exit(exit_code)

    target_date = args.date or today_ar()
    exit_code = run_for_date(target_date, gate=args.gate, use_judge=args.judge, on_fail=args.on_fail)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
