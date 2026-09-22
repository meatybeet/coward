#!/bin/sh
#
# Put the dependencies in ./libs so the app needs nothing installed on the node.
#
# Why this exists: a hosting node carries nginx, quota and python3 — no pip, no venv
# module — and an account has no root to add them. Vendoring sidesteps that: pip runs
# on YOUR machine and the result travels with your code.
#
# The platform flags matter. Without them, pip on Windows or macOS downloads wheels
# for Windows or macOS, which will not import on the node. These ask for Linux x86-64
# wheels for the Python the node runs (3.10 on Ubuntu 22.04 — check with
# `ssh <account>@<node-ip> python3 -V` and adjust).
#
# Flask, Werkzeug, Jinja2, click, itsdangerous, blinker and gunicorn are pure Python,
# so this is clean. A package with C extensions needs a manylinux wheel to exist; if
# pip says it cannot find one, that dependency needs a venv built on the node instead.
set -e
cd "$(dirname "$0")"

PY_VERSION="${1:-3.10}"

rm -rf libs
pip install \
  --target libs \
  --only-binary=:all: \
  --platform manylinux2014_x86_64 \
  --python-version "$PY_VERSION" \
  -r requirements.txt

# Not needed at runtime and they bloat the upload.
rm -rf libs/*.dist-info/RECORD libs/bin
echo
echo "libs/ built for linux x86-64, python $PY_VERSION"
du -sh libs 2>/dev/null || true
