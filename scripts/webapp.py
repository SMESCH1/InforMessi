#!/usr/bin/env python3
"""
Interfaz web editorial para InforMessi.
Permite revisar y editar los próximos 15 informes antes de publicarlos.

Uso:
    python scripts/webapp.py          # Puerto 5001
    WEBAPP_PORT=8080 python scripts/webapp.py
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from flask import Flask, request, jsonify, render_template_string
except ImportError:
    print("ERROR: Flask no instalado. Ejecuta: pip install flask")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_report(date_str: str) -> dict:
    path = REPORTS_DIR / f"{date_str}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_report(date_str: str, report: dict) -> bool:
    path = REPORTS_DIR / f"{date_str}.json"
    try:
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception:
        return False


def _status_badge(status: str) -> str:
    colors = {
        "draft": "secondary",
        "updated": "primary",
        "pre_approved": "success",
        "published": "dark",
    }
    color = colors.get(status, "light")
    return f'<span class="badge bg-{color}">{status or "sin estado"}</span>'


def _get_dashboard_rows() -> list:
    rows = []
    today = datetime.now().date()
    for i in range(15):
        d = today + timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        report = _load_report(date_str)
        message = report.get("message", "")
        preview = (message[:60] + "…") if len(message) > 60 else message
        data = report.get("data", {})
        events_count = len(data.get("events", []))
        news_count = len(data.get("news", []))
        status = report.get("status", "")
        rows.append({
            "date": date_str,
            "weekday": d.strftime("%A"),
            "status": status,
            "status_badge": _status_badge(status),
            "preview": preview or "<em class='text-muted'>Sin mensaje</em>",
            "events": events_count,
            "news": news_count,
            "exists": bool(report),
        })
    return rows


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

BASE_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>InforMessi Editorial</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <style>
    body { font-family: monospace; }
    .table td { vertical-align: middle; }
    .word-count-ok { color: green; font-weight: bold; }
    .word-count-bad { color: red; font-weight: bold; }
    .spinner-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,.4);
                       z-index:9999; align-items:center; justify-content:center; }
    .spinner-overlay.active { display:flex; }
  </style>
</head>
<body>
<nav class="navbar navbar-dark bg-dark px-3">
  <a class="navbar-brand" href="/">⚽ InforMessi Editorial</a>
</nav>
<div class="container-fluid py-3">
{% block content %}{% endblock %}
</div>
<div class="spinner-overlay" id="spinnerOverlay">
  <div class="text-center text-white">
    <div class="spinner-border mb-2" role="status"></div>
    <div>Regenerando mensaje…</div>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
{% block scripts %}{% endblock %}
</body>
</html>"""

DASHBOARD_TEMPLATE = BASE_HTML.replace("{% block content %}{% endblock %}", """
<h4 class="mb-3">Próximos 15 días</h4>
<table class="table table-hover table-sm">
  <thead class="table-dark">
    <tr>
      <th>Fecha</th><th>Día</th><th>Estado</th><th>Preview</th>
      <th class="text-center">Eventos</th><th class="text-center">Noticias</th><th>Acciones</th>
    </tr>
  </thead>
  <tbody>
  {% for row in rows %}
  <tr style="cursor:pointer" onclick="location.href='/report/{{ row.date }}'">
    <td>{{ row.date }}</td>
    <td>{{ row.weekday }}</td>
    <td>{{ row.status_badge | safe }}</td>
    <td>{{ row.preview | safe }}</td>
    <td class="text-center">{{ row.events }}</td>
    <td class="text-center">{{ row.news }}</td>
    <td>
      <a href="/report/{{ row.date }}" class="btn btn-sm btn-outline-primary">Editar</a>
    </td>
  </tr>
  {% endfor %}
  </tbody>
</table>
""")

EDIT_TEMPLATE = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="mb-2">
  <a href="/" class="btn btn-sm btn-outline-secondary">← Dashboard</a>
  <span class="ms-3 fw-bold fs-5">{{ date }} — {{ weekday }}</span>
  <span class="ms-2">{{ status_badge | safe }}</span>
</div>
<div class="row g-3">
  <!-- Columna izquierda: editor -->
  <div class="col-md-6">
    <div class="card h-100">
      <div class="card-header d-flex justify-content-between align-items-center">
        <strong>Mensaje</strong>
        <span id="wordCount" class="badge bg-secondary">0 palabras</span>
      </div>
      <div class="card-body d-flex flex-column">
        <textarea id="messageEditor" class="form-control flex-grow-1" rows="14"
          style="font-size:0.85rem">{{ message }}</textarea>
        <div class="mt-2 d-flex gap-2 flex-wrap">
          <button class="btn btn-success btn-sm" onclick="saveMessage()">💾 Guardar</button>
          <button class="btn btn-primary btn-sm" onclick="preApprove()">✅ Pre-aprobar</button>
          <button class="btn btn-warning btn-sm" onclick="regenerate()">🔄 Regenerar</button>
          <button class="btn btn-outline-secondary btn-sm" onclick="resetMessage()">↩ Reset</button>
        </div>
        <div id="actionResult" class="mt-2 text-muted small"></div>
      </div>
    </div>
  </div>
  <!-- Columna derecha: contexto -->
  <div class="col-md-6">
    <!-- Eventos -->
    <div class="card mb-3">
      <div class="card-header"><strong>Eventos disponibles ({{ events | length }})</strong></div>
      <div class="card-body p-2">
        {% if events %}
          {% for e in events %}
          <div class="border-bottom pb-1 mb-1 small">
            <span class="badge bg-info text-dark">{{ e.get('type','?') }}</span>
            {{ e.get('description', e.get('person', ''))[:120] }}
          </div>
          {% endfor %}
        {% else %}
          <em class="text-muted">Sin eventos</em>
        {% endif %}
      </div>
    </div>
    <!-- Noticias -->
    <div class="card mb-3">
      <div class="card-header"><strong>Noticias disponibles ({{ news | length }})</strong></div>
      <div class="card-body p-2">
        {% if news %}
          {% for n in news %}
          <div class="border-bottom pb-1 mb-1 small">
            <span class="badge bg-secondary">{{ n.get('source','?') }}</span>
            {% set score = n.get('freshness_score', 0.5) %}
            {% if score >= 1.0 %}<span class="badge bg-success">[HOY]</span>
            {% elif score >= 0.8 %}<span class="badge bg-primary">[AYER]</span>
            {% elif score >= 0.5 %}<span class="badge bg-warning text-dark">[2d]</span>
            {% else %}<span class="badge bg-danger">[+3d]</span>{% endif %}
            {{ n.get('title','')[:100] }}
          </div>
          {% endfor %}
        {% else %}
          <em class="text-muted">Sin noticias</em>
        {% endif %}
      </div>
    </div>
    <!-- Memoria -->
    <div class="card">
      <div class="card-header"><strong>Memoria (bloqueados recientes)</strong></div>
      <div class="card-body p-2 small">
        {% if blocked_news %}
          <div class="mb-1 fw-bold text-danger">⛔ Noticias bloqueadas:</div>
          {% for n in blocked_news[:8] %}
            <div class="text-muted">• {{ n }}</div>
          {% endfor %}
        {% endif %}
        {% if blocked_events %}
          <div class="mt-2 mb-1 fw-bold text-danger">⛔ Eventos bloqueados:</div>
          {% for e in blocked_events[:8] %}
            <div class="text-muted">• {{ e }}</div>
          {% endfor %}
        {% endif %}
        {% if not blocked_news and not blocked_events %}
          <em class="text-muted">Sin bloqueos recientes</em>
        {% endif %}
      </div>
    </div>
  </div>
</div>
""").replace("{% block scripts %}{% endblock %}", """
<script>
const DATE = "{{ date }}";
const originalMessage = {{ message_json | safe }};

const editor = document.getElementById('messageEditor');
const wordCountEl = document.getElementById('wordCount');
const actionResult = document.getElementById('actionResult');

function updateWordCount() {
  const words = editor.value.trim().split(/\\s+/).filter(w => w.length > 0).length;
  wordCountEl.textContent = words + ' palabras';
  if (words >= 90 && words <= 130) {
    wordCountEl.className = 'badge bg-success';
  } else {
    wordCountEl.className = 'badge bg-danger';
  }
}

editor.addEventListener('input', updateWordCount);
updateWordCount();

function showResult(msg, ok=true) {
  actionResult.textContent = msg;
  actionResult.className = ok ? 'mt-2 text-success small' : 'mt-2 text-danger small';
}

async function saveMessage() {
  const res = await fetch(`/api/report/${DATE}/save`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: editor.value})
  });
  const data = await res.json();
  showResult(data.ok ? '✅ Guardado.' : '❌ Error al guardar.', data.ok);
}

async function preApprove() {
  const res = await fetch(`/api/report/${DATE}/pre-approve`, {method: 'POST'});
  const data = await res.json();
  if (data.ok) {
    showResult(data.pre_approved ? '✅ Pre-aprobado.' : '↩ Vuelto a draft.', true);
    setTimeout(() => location.reload(), 800);
  } else {
    showResult('❌ Error.', false);
  }
}

async function regenerate() {
  document.getElementById('spinnerOverlay').classList.add('active');
  actionResult.textContent = '';
  const res = await fetch(`/api/report/${DATE}/regenerate`, {method: 'POST'});
  document.getElementById('spinnerOverlay').classList.remove('active');
  const data = await res.json();
  if (data.ok && data.message) {
    editor.value = data.message;
    updateWordCount();
    showResult('✅ Mensaje regenerado.', true);
  } else {
    showResult('❌ Error al regenerar: ' + (data.error || ''), false);
  }
}

function resetMessage() {
  editor.value = originalMessage;
  updateWordCount();
  showResult('↩ Mensaje reseteado al original.', true);
}
</script>
""")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    rows = _get_dashboard_rows()
    return render_template_string(DASHBOARD_TEMPLATE, rows=rows)


@app.route("/report/<date_str>")
def edit_report(date_str: str):
    report = _load_report(date_str)
    message = report.get("message", "")
    data = report.get("data", {})
    status = report.get("status", "draft")

    # Load blocked items from memory
    blocked_news, blocked_events = [], []
    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        from rag_memory_database import MemoryDatabase
        from datetime import datetime as _dt

        db = MemoryDatabase()
        today = _dt.now().date()

        for key, dates in db.data.get("news_topics", {}).items():
            parsed = []
            for d in dates:
                try:
                    parsed.append(_dt.strptime(d, "%Y-%m-%d").date())
                except Exception:
                    pass
            if parsed and (today - max(parsed)).days <= 7:
                blocked_news.append(key)

        for key, dates in db.data.get("events_mentioned", {}).items():
            parsed = []
            for d in dates:
                try:
                    parsed.append(_dt.strptime(d, "%Y-%m-%d").date())
                except Exception:
                    pass
            if parsed and (today - max(parsed)).days <= 14:
                blocked_events.append(key)
    except Exception:
        pass

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = d.strftime("%A")
    except Exception:
        weekday = ""

    return render_template_string(
        EDIT_TEMPLATE,
        date=date_str,
        weekday=weekday,
        status_badge=_status_badge(status),
        message=message,
        message_json=json.dumps(message),
        events=data.get("events", []),
        news=data.get("news", []),
        blocked_news=blocked_news,
        blocked_events=blocked_events,
    )


@app.route("/api/report/<date_str>/save", methods=["POST"])
def api_save(date_str: str):
    body = request.get_json(force=True, silent=True) or {}
    new_message = body.get("message", "")
    report = _load_report(date_str)
    if not report:
        report = {"date": date_str, "status": "draft", "data": {}}
    report["message"] = new_message
    ok = _save_report(date_str, report)
    return jsonify({"ok": ok})


@app.route("/api/report/<date_str>/pre-approve", methods=["POST"])
def api_pre_approve(date_str: str):
    report = _load_report(date_str)
    if not report:
        return jsonify({"ok": False, "error": "Report not found"})
    current = report.get("status", "draft")
    if current == "pre_approved":
        report["status"] = "draft"
        pre_approved = False
    else:
        report["status"] = "pre_approved"
        pre_approved = True
    ok = _save_report(date_str, report)
    return jsonify({"ok": ok, "pre_approved": pre_approved})


@app.route("/api/report/<date_str>/regenerate", methods=["POST"])
def api_regenerate(date_str: str):
    report = _load_report(date_str)
    if not report:
        return jsonify({"ok": False, "error": "Report not found"})

    # Find the data file for this date
    data_file = PROJECT_ROOT / "tmp" / f"data-{date_str}.json"
    if not data_file.exists():
        # Try to use embedded data from the report itself
        data = report.get("data")
        if data:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            )
            json.dump({**data, "date": date_str,
                       "mundial_2026_start": "2026-06-11"}, tmp, ensure_ascii=False)
            tmp.close()
            data_file = Path(tmp.name)
        else:
            return jsonify({"ok": False, "error": f"No data file for {date_str}"})

    provider = os.environ.get("LLM_PROVIDER", "ollama")
    model = os.environ.get("LLM_MODEL", "qwen2.5:7b-instruct")

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "generate-message.py"),
                "--data", str(data_file),
                "--provider", provider,
                "--model", model,
            ],
            capture_output=True, text=True, timeout=90
        )
        stdout = result.stdout
        # Extract message between separators
        marker = "=" * 50
        parts = stdout.split(marker)
        message = ""
        for i, part in enumerate(parts):
            if "MENSAJE GENERADO" in part and i + 1 < len(parts):
                message = parts[i + 1].strip()
                break
        if not message:
            message = stdout.strip()

        if message:
            report["message"] = message
            _save_report(date_str, report)
            return jsonify({"ok": True, "message": message})
        else:
            return jsonify({"ok": False, "error": result.stderr[:300] or "No message generated"})
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "Timeout (90s) al regenerar"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("WEBAPP_PORT", 5001))
    print(f"🌐 InforMessi Editorial — http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
