"""
Entry point.

Two jobs, and both exist because of how a proxy site is run:

  * `app` at module level, so gunicorn can be pointed at `main:app`.
  * a `__main__` block that reads PORT, so `python3 main.py` also works — useful
    before you have gunicorn, and for a quick check over SSH.

The port is never hardcoded. The deploy allocates one port per site and writes it
into the systemd unit as `Environment=PORT=...`; nginx proxies to 127.0.0.1 on that
port. Two sites on the same node get different ports.

`libs/` is put on the path first: it is where vendored dependencies land if you
choose that route over a venv (see vendor.sh). Absent, this line does nothing.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VENDORED = os.path.join(HERE, "libs")
if os.path.isdir(VENDORED) and VENDORED not in sys.path:
    sys.path.insert(0, VENDORED)

from app import create_app  # noqa: E402  (must follow the sys.path line above)

app = create_app()


if __name__ == "__main__":
    # 127.0.0.1 because nginx is the only thing that should reach this process.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8000")))
