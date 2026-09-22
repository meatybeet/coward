"""API routes. An ordinary Flask blueprint."""
import os
import platform
import sys
import time

from flask import Blueprint, jsonify, request

from app.store import add_item, list_items

api = Blueprint("api", __name__)

STARTED = time.time()


@api.get("/")
def index():
    """A page rather than JSON, so opening the site in a browser shows something."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Flask API — WAYHOST hosting</title>
<style>
  body{{margin:0;padding:40px 20px;font:16px/1.6 system-ui,sans-serif;background:#f2f5fb;color:#1a2b4b}}
  main{{max-width:700px;margin:0 auto;background:#fff;border:1px solid #e2e8f3;border-radius:12px;padding:28px 32px}}
  h1{{margin:0 0 6px;font-size:24px}}
  h2{{margin:26px 0 8px;font-size:16px;color:#5b6b8a}}
  table{{width:100%;border-collapse:collapse;font-size:14px}}
  td{{padding:7px 0;border-bottom:1px solid #eef1f7}}
  td:first-child{{color:#5b6b8a;width:200px}}
  code{{font-family:ui-monospace,monospace;background:#f2f5fb;padding:1px 5px;border-radius:4px;font-size:.9em}}
  a{{color:#2b73f4}}
  .badge{{display:inline-block;background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:700}}
</style>
</head>
<body>
<main>
  <h1>Flask API is running <span class="badge">proxy</span></h1>
  <p>A full project folder — <code>main.py</code>, <code>app/</code>,
     <code>requirements.txt</code> — behind nginx.</p>

  <h2>Process</h2>
  <table>
    <tr><td>Python</td><td><code>{platform.python_version()}</code></td></tr>
    <tr><td>Interpreter</td><td><code>{sys.executable}</code></td></tr>
    <tr><td>PID</td><td><code>{os.getpid()}</code></td></tr>
    <tr><td>PORT from environment</td><td><code>{os.environ.get('PORT', '(unset)')}</code></td></tr>
    <tr><td>Working directory</td><td><code>{os.getcwd()}</code></td></tr>
    <tr><td>Where Flask came from</td><td><code>{_flask_origin()}</code></td></tr>
    <tr><td>Uptime</td><td><code>{round(time.time() - STARTED, 1)}s</code></td></tr>
  </table>

  <h2>Through nginx</h2>
  <table>
    <tr><td>Host</td><td><code>{request.headers.get('Host', '-')}</code></td></tr>
    <tr><td>X-Real-IP</td><td><code>{request.headers.get('X-Real-IP', '-')}</code></td></tr>
    <tr><td>X-Forwarded-For</td><td><code>{request.headers.get('X-Forwarded-For', '-')}</code></td></tr>
  </table>

  <h2>Endpoints</h2>
  <ul>
    <li><a href="/health">GET /health</a></li>
    <li><a href="/api/items">GET /api/items</a> — reads SQLite</li>
    <li><code>POST /api/items</code> with <code>{{"name": "..."}}</code> — writes SQLite</li>
    <li><a href="/api/whoami">GET /api/whoami</a></li>
  </ul>
  <pre style="background:#0d1117;color:#79c0ff;padding:12px 14px;border-radius:8px;overflow-x:auto;font-size:13px">curl -s -X POST https://{request.headers.get('Host', 'your-domain')}/api/items \
  -H 'Content-Type: application/json' -d '{{"name":"first"}}'</pre>
</main>
</body>
</html>"""


def _flask_origin():
    """Whether Flask was imported from a venv, from vendored libs/, or system-wide."""
    import flask
    path = os.path.dirname(os.path.dirname(flask.__file__))
    if f"{os.sep}libs" in path or path.endswith("libs"):
        return f"vendored libs/ ({path})"
    if "venv" in path or "site-packages" in path:
        return path
    return path


@api.get("/health")
def health():
    return jsonify(
        status="ok",
        pid=os.getpid(),
        port=os.environ.get("PORT"),
        uptime_seconds=round(time.time() - STARTED, 1),
    )


@api.get("/api/items")
def get_items():
    return jsonify(items=list_items())


@api.post("/api/items")
def post_item():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify(error="name is required"), 400
    return jsonify(item=add_item(name)), 201


@api.get("/api/whoami")
def whoami():
    """Proves which Unix account the process runs as: your own, not www-data."""
    return jsonify(
        uid=getattr(os, "geteuid", lambda: None)(),
        user=os.environ.get("USER") or os.path.basename(os.path.expanduser("~")),
        home=os.environ.get("HOME"),
        cwd=os.getcwd(),
    )
