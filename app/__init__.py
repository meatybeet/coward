"""
Flask application factory.

Nothing here is hosting-specific: this is an ordinary Flask package. What makes it
run on a hosting node is main.py (which reads PORT) and start.sh (which is what the
site's `command` points at).
"""
from flask import Flask

from app.routes import api
from app.store import init_db


def create_app():
    app = Flask(__name__)

    # SQLite lives next to the code, inside the account's home, so it counts against
    # the disk quota like everything else. It is also the only database available:
    # the node has no MySQL and no per-account database is created.
    init_db()

    app.register_blueprint(api)
    return app
