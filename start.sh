#!/bin/sh
#
# What the site's `command` points at:
#
#     /bin/sh start.sh
#
# Why a script at all: a proxy `command` is validated against a plain character set
# with no `$` in it, so `--bind 127.0.0.1:$PORT` cannot go in the command itself. In
# here, ordinary shell rules apply and $PORT is just an environment variable. It is
# run as `/bin/sh start.sh` rather than `./start.sh` because an uploaded file arrives
# without the execute bit.
#
# systemd runs this with WorkingDirectory set to the site directory, so relative
# paths are fine. `exec` matters: it replaces the shell with the server, so systemd
# supervises the real process and `systemctl restart` stops the right thing.
set -e

PORT="${PORT:-8000}"

# Vendored dependencies, if that is how they got here.
if [ -d libs ]; then
  PYTHONPATH="$PWD/libs${PYTHONPATH:+:$PYTHONPATH}"
  export PYTHONPATH
fi

# A venv wins when there is one; otherwise the system interpreter.
if [ -x venv/bin/python ]; then
  PY=venv/bin/python
else
  PY=/usr/bin/python3
fi

# gunicorn if it is importable, the Flask dev server if not. The dev server is
# single-threaded and warns about itself, but it is enough to prove the site works.
if "$PY" -c 'import gunicorn' >/dev/null 2>&1; then
  echo "starting gunicorn on 127.0.0.1:$PORT"
  exec "$PY" -m gunicorn --bind "127.0.0.1:$PORT" --workers 2 --timeout 60 main:app
fi

echo "gunicorn not available, falling back to the Flask dev server on 127.0.0.1:$PORT"
exec "$PY" main.py
