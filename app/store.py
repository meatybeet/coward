"""
A SQLite store, because it is the database you actually have.

No MySQL server is installed on a hosting node and no per-account database is
created, so a file in the site directory is the working answer for small apps. It
inherits the account's disk quota and its backups are whatever you copy over SFTP.
"""
import os
import sqlite3

# Beside the code, inside the site directory. A proxy site's directory is never
# served by nginx (the vhost has no `root`), so the file is not reachable over HTTP.
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.db")


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS items ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " name TEXT NOT NULL,"
            " created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )


def list_items():
    with connect() as connection:
        rows = connection.execute(
            "SELECT id, name, created_at FROM items ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return [dict(row) for row in rows]


def add_item(name):
    with connect() as connection:
        cursor = connection.execute("INSERT INTO items (name) VALUES (?)", (name,))
        item_id = cursor.lastrowid
        row = connection.execute(
            "SELECT id, name, created_at FROM items WHERE id = ?", (item_id,)
        ).fetchone()
    return dict(row)
